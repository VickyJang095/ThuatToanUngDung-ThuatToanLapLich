import math
import random
import unittest
from unittest.mock import patch

import app
from scheduling.jobs import DEADLINE_RANGES, random_jobs


class RandomJobsTests(unittest.TestCase):
    def test_ranges_for_all_levels_and_machine_counts(self):
        for level, (low, high) in DEADLINE_RANGES.items():
            for machines in (1, 3, 20):
                for n in (0, 1, 10, 30):
                    with self.subTest(level=level, machines=machines, n=n):
                        random.seed(123)
                        jobs = random_jobs(n, machines=machines, deadline_level=level)
                        self.assertEqual(len(jobs), n)
                        if not jobs:
                            continue
                        horizon = max(max(j["p"] for j in jobs), sum(j["p"] for j in jobs) / machines)
                        for i, job in enumerate(jobs):
                            self.assertEqual(job["id"], i + 1)
                            self.assertTrue(3 <= job["p"] <= 20)
                            self.assertTrue(1 <= job["w"] <= 5)
                            lower = max(job["p"], math.ceil(low * horizon))
                            upper = max(lower, math.floor(high * horizon))
                            self.assertIsInstance(job["d"], int)
                            self.assertTrue(lower <= job["d"] <= upper)

    def test_same_seed_keeps_workload_across_levels(self):
        batches = []
        for level in DEADLINE_RANGES:
            random.seed(42)
            batches.append(random_jobs(10, deadline_level=level))
        workload = lambda jobs: [(j["p"], j["w"]) for j in jobs]
        self.assertEqual(workload(batches[0]), workload(batches[1]))
        self.assertEqual(workload(batches[1]), workload(batches[2]))

    def test_generate_api_passes_machine_count_and_level(self):
        with patch("web.routes.random_jobs", return_value=[]) as generate:
            with app.app.test_client() as client:
                response = client.post("/api/generate", json={"machines": 7, "jobs": 12, "deadline_level": "tight"})
        self.assertEqual(response.status_code, 200)
        generate.assert_called_once_with(12, machines=7, deadline_level="tight")

    def test_invalid_level_is_rejected(self):
        with app.app.test_client() as client:
            response = client.post("/api/generate", json={"deadline_level": "invalid"})
        self.assertEqual(response.status_code, 400)

    def test_service_fallback_uses_machine_count(self):
        with patch("scheduling.service.random_jobs", return_value=[]) as generate:
            app.run_algorithms(5, [], jobs_count=0, pop_size=10, generations=2)
        generate.assert_called_once_with(0, machines=5)


if __name__ == "__main__":
    unittest.main()
