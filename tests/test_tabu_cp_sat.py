import builtins
import itertools
import random
import unittest
from unittest.mock import patch

from scheduling.cp_sat import cp_sat
from scheduling.tabu_search import tabu_search
from scheduling.genetic import decode_permutation
from scheduling.branch_and_bound import branch_and_bound
from scheduling.service import run_algorithms
from scheduling.metrics import evaluate_schedule


def brute_force(jobs, machines):
    # Độc lập với decoder: duyệt mọi thứ tự và mọi cách phân máy.
    best = float("inf")
    for order in itertools.permutations(range(len(jobs))):
        for assignment in itertools.product(range(machines), repeat=len(jobs)):
            times = [0] * machines
            cost = 0
            for i, m in zip(order, assignment):
                job = jobs[i]
                times[m] += job["p"]
                cost += job["w"] * max(0, times[m] - job["d"])
            best = min(best, cost)
    return best


class SolverTests(unittest.TestCase):
    def check_schedule(self, result, jobs, machines):
        schedule = result["schedule"]
        self.assertEqual(len(schedule), machines)
        seen = []
        for m, row in enumerate(schedule):
            last_end = 0
            for task in row:
                original = next(j for j in jobs if j["id"] == task["id"])
                for field in ("p", "d", "w"):
                    self.assertEqual(task[field], original[field])
                self.assertGreaterEqual(task["start"], 0)
                self.assertEqual(task["end"] - task["start"], original["p"])
                self.assertEqual(task["machine"], m + 1)
                if task["p"] > 0:
                    self.assertGreaterEqual(task["start"], last_end)
                    last_end = task["end"]
                seen.append(task["id"])
        self.assertCountEqual(seen, [j["id"] for j in jobs])
        self.assertEqual(evaluate_schedule(schedule)["objective"], result["objective"])

    def test_small_instances_against_independent_enumeration(self):
        rng = random.Random(98)
        for n in range(1, 6):
            jobs = [dict(id=i, p=rng.randint(0, 5), d=rng.randint(-2, 7),
                         w=rng.randint(0, 4)) for i in range(n)]
            for machines in (1, 2):
                with self.subTest(n=n, machines=machines):
                    expected = brute_force(jobs, machines)
                    cp = cp_sat(jobs, machines)
                    self.assertEqual(cp["status"], "OPTIMAL")
                    self.assertTrue(cp["optimal"])
                    self.assertEqual(cp["objective"], expected)
                    self.assertEqual(cp["best_bound"], expected)
                    self.check_schedule(cp, jobs, machines)
                    # B&B đã được xác nhận có cả hai vòng duyệt trong mã nguồn.
                    self.assertEqual(branch_and_bound(jobs, machines)["objective"], expected)
                    ts = tabu_search(jobs, machines)
                    edd = sorted(range(n), key=lambda i: jobs[i]["d"])
                    self.assertLessEqual(ts["objective"], decode_permutation(edd, jobs, machines)[0])
                    self.check_schedule(ts, jobs, machines)

    def test_empty_single_and_extra_machines(self):
        for jobs in ([], [dict(id=1, p=3, d=-1, w=2)],
                     [dict(id=i, p=0, d=-2, w=1) for i in range(3)]):
            for machines in (1, 5):
                for solver in (tabu_search, cp_sat):
                    self.check_schedule(solver(jobs, machines), jobs, machines)
                result = run_algorithms(machines, jobs, jobs_count=0, pop_size=10, generations=2)
                for key in ("ts", "cp_sat", "ga"):
                    raw = {**result[key], "schedule": [r["jobs"] for r in result[key]["schedule"]]}
                    self.check_schedule(raw, jobs, machines)

    def test_branch_and_bound_timeout_returns_feasible_schedule(self):
        jobs = [dict(id=i, p=5, d=5, w=1) for i in range(6)]
        result = branch_and_bound(jobs, 2, time_limit=0)
        self.assertEqual(result["status"], "TIME_LIMIT")
        self.assertFalse(result["optimal"])
        self.check_schedule(result, jobs, 2)

    def test_validation(self):
        for field in ("p", "d", "w"):
            for value in (1.5, 1.0, True, "2"):
                job = dict(id=1, p=2, d=3, w=1)
                job[field] = value
                with self.assertRaises(ValueError):
                    cp_sat([job], 1)
        for field in ("p", "w"):
            job = dict(id=1, p=2, d=3, w=1)
            job[field] = -1
            with self.assertRaises(ValueError):
                cp_sat([job], 1)

    def test_no_solution_retains_null(self):
        jobs = [dict(id=i, p=2, d=1, w=1) for i in range(6)]
        result = cp_sat(jobs, 2, time_limit=0)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertIsNone(result["objective"])
        self.assertIsNone(result["schedule"])
        self.assertFalse(result["optimal"])
        with patch("scheduling.service.cp_sat", return_value=result):
            payload = run_algorithms(2, jobs, pop_size=10, generations=2)
        self.assertIsNone(payload["cp_sat"]["objective"])
        self.assertIsNone(payload["cp_sat"]["schedule"])
        self.assertEqual(payload["cp_sat"]["best_bound"], result["best_bound"])

    def test_missing_ortools(self):
        real_import = builtins.__import__
        def without_ortools(name, *args, **kwargs):
            if name.startswith("ortools"):
                raise ImportError("simulated missing dependency")
            return real_import(name, *args, **kwargs)
        jobs = [dict(id=1, p=2, d=1, w=1)]
        with patch("builtins.__import__", side_effect=without_ortools):
            payload = run_algorithms(2, jobs, pop_size=10, generations=2)
        cp = payload["cp_sat"]
        self.assertEqual(cp["status"], "UNAVAILABLE")
        self.assertIn("pip install", cp["message"])
        self.assertIsNone(cp["objective"])
        self.assertIsNone(cp["schedule"])
        self.assertFalse(cp["optimal"])
        self.assertIsNotNone(payload["ts"]["schedule"])
        self.assertIsNotNone(payload["ga"]["schedule"])

    def test_feasible_and_unavailable_json(self):
        import app
        jobs = [dict(id=1, p=2, d=1, w=1)]
        feasible = cp_sat(jobs, 1)
        feasible.update(status="FEASIBLE", optimal=False, best_bound=0.0)
        unavailable = dict(objective=None, schedule=None, status="UNAVAILABLE",
                           optimal=False, best_bound=None, message="pip install -r requirements.txt")
        for result in (feasible, unavailable):
            with patch("scheduling.service.cp_sat", return_value=result):
                with app.app.test_client() as client:
                    response = client.post("/api/run", json={"machines": 1, "jobs": jobs,
                                           "population": 10, "generations": 2})
            self.assertEqual(response.status_code, 200)
            cp = response.get_json()["cp_sat"]
            for field in ("objective", "status", "best_bound", "optimal"):
                self.assertEqual(cp[field], result[field])

    def test_tabu_expiry_and_aspiration(self):
        jobs = [dict(id=i, p=1, d=i, w=1) for i in range(2)]
        # Với hai việc, bước đảo ngược duy nhất bị cấm nên dừng rõ ràng.
        with patch("scheduling.tabu_search.decode_permutation", return_value=(10, [[]])) as decode:
            tabu_search(jobs, 1, max_iterations=20, tabu_tenure=7)
            self.assertEqual(decode.call_count, 3)
        # Aspiration cho phép đảo ngược bị tabu nếu cải thiện toàn cục.
        with patch("scheduling.tabu_search.decode_permutation",
                   side_effect=[(10, [[]]), (12, [[]]), (8, [[]])]):
            result = tabu_search(jobs, 1, max_iterations=2)
            self.assertEqual(result["objective"], 8)
        with patch("scheduling.tabu_search.decode_permutation", return_value=(10, [[]])) as decode:
            tabu_search(jobs, 1, max_iterations=4, tabu_tenure=0)
            self.assertEqual(decode.call_count, 5)


if __name__ == "__main__":
    unittest.main()
