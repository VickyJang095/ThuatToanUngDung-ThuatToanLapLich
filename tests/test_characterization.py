import random
import unittest

import app


JOBS = [
    {"id": 1, "p": 4, "d": 5, "w": 2},
    {"id": 2, "p": 3, "d": 10, "w": 1},
    {"id": 3, "p": 7, "d": 8, "w": 3},
    {"id": 4, "p": 2, "d": 7, "w": 4},
]


def assert_valid_schedule(test_case, schedule, jobs, machines):
    scheduled_jobs = []
    for machine_index, machine_jobs in enumerate(schedule):
        previous_end = 0
        for job in machine_jobs:
            test_case.assertEqual(job["machine"], machine_index + 1)
            test_case.assertEqual(job["start"], previous_end)
            test_case.assertEqual(job["end"] - job["start"], job["p"])
            previous_end = job["end"]
            scheduled_jobs.append(job["id"])

    test_case.assertEqual(len(schedule), machines)
    test_case.assertCountEqual(scheduled_jobs, [job["id"] for job in jobs])


class SchedulingCharacterizationTests(unittest.TestCase):
    def test_greedy_policies_and_lpt_compatibility(self):
        expected_ids = {
            "lpt": [[3, 4], [1, 2]],
            "edd": [[1, 2], [4, 3]],
            "wspt": [[4, 3], [1, 2]],
        }
        expected_objectives = {"lpt": 8, "edd": 3, "wspt": 3}

        for policy in ("lpt", "edd", "wspt"):
            with self.subTest(policy=policy):
                schedule = app.greedy_schedule(JOBS, 2, policy)
                self.assertEqual(
                    [[job["id"] for job in row] for row in schedule],
                    expected_ids[policy],
                )
                result = app.evaluate_schedule(schedule)
                self.assertEqual(result["objective"], expected_objectives[policy])
                self.assertEqual(result["makespan"], 9)
                assert_valid_schedule(self, schedule, JOBS, 2)

        self.assertEqual(app.schedule_lpt(JOBS, 2), app.greedy_schedule(JOBS, 2, "lpt"))
        lpt_metrics = app.evaluate_schedule(app.schedule_lpt(JOBS, 2))
        self.assertEqual((lpt_metrics["objective"], lpt_metrics["makespan"]), (8, 9))

    def test_genetic_algorithm_seeded_result(self):
        random.seed(2718)
        result = app.genetic_algorithm(
            JOBS,
            2,
            pop_size=10,
            generations=8,
            crossover_rate=0.8,
            mutation_rate=0.1,
        )

        self.assertEqual(result["objective"], 0)
        self.assertEqual(
            [[(job["id"], job["start"], job["end"]) for job in row]
             for row in result["schedule"]],
            [[(1, 0, 4), (4, 4, 6), (2, 6, 9)], [(3, 0, 7)]],
        )
        metrics = app.evaluate_schedule(result["schedule"])
        self.assertEqual((metrics["objective"], metrics["makespan"]), (0, 9))
        assert_valid_schedule(self, result["schedule"], JOBS, 2)


class ApiCharacterizationTests(unittest.TestCase):
    def test_home_and_generate_endpoints(self):
        with app.app.test_client() as client:
            home_response = client.get("/")
            self.assertEqual(home_response.status_code, 200)

            response = client.post("/api/generate", json={"machines": 2, "jobs": 3})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(set(payload), {"machines", "jobs"})
        self.assertEqual(payload["machines"], 2)
        self.assertEqual(len(payload["jobs"]), 3)
        self.assertTrue(all(set(job) == {"id", "p", "d", "w"} for job in payload["jobs"]))

    def test_run_endpoint_schema_and_schedule_metrics(self):
        random.seed(2718)
        with app.app.test_client() as client:
            response = client.post(
                "/api/run",
                json={
                    "machines": 2,
                    "jobs": JOBS,
                    "population": 10,
                    "generations": 8,
                    "crossover": 0.8,
                    "mutation": 0.1,
                },
            )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(
            set(payload), {"machines", "jobs", "greedy", "lpt", "ga", "bb", "ts", "cp_sat"}
        )
        self.assertEqual(set(payload["greedy"]), {
            "best_policy", "objective", "makespan", "schedule", "runtime", "policies"
        })
        for algorithm in ("lpt", "ga", "bb"):
            with self.subTest(algorithm=algorithm):
                expected_keys = {"objective", "makespan", "schedule", "runtime"}
                if algorithm == "bb":
                    expected_keys.update({"available", "status", "optimal"})
                self.assertEqual(set(payload[algorithm]), expected_keys)
                self.assert_valid_serialized_schedule(payload[algorithm]["schedule"])

        self.assertEqual(set(payload["greedy"]["policies"]), {"lpt", "edd", "wspt"})
        self.assertEqual(payload["greedy"]["objective"], 3)
        self.assertEqual(payload["greedy"]["makespan"], 9)
        self.assertEqual(payload["lpt"]["objective"], 8)
        self.assertEqual(payload["ga"]["objective"], 0)
        self.assertEqual(payload["bb"]["objective"], 0)
        self.assertTrue(payload["bb"]["available"])

    def assert_valid_serialized_schedule(self, serialized_schedule):
        self.assertEqual(len(serialized_schedule), 2)
        schedule = [machine["jobs"] for machine in serialized_schedule]
        for machine_index, machine in enumerate(serialized_schedule):
            self.assertEqual(machine["machine"], machine_index + 1)
        assert_valid_schedule(self, schedule, JOBS, 2)


if __name__ == "__main__":
    unittest.main()