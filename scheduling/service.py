import time

from scheduling.branch_and_bound import branch_and_bound
from scheduling.genetic import genetic_algorithm
from scheduling.greedy import greedy_schedule, schedule_lpt
from scheduling.jobs import random_jobs
from scheduling.metrics import evaluate_schedule
from scheduling.tabu_search import tabu_search
from scheduling.cp_sat import cp_sat


def serialize_schedule(schedule):
    return [{
        "machine": i + 1,
        "jobs": jobs,
    } for i, jobs in enumerate(schedule)]


def run_algorithms(
    machine_count,
    jobs,
    pop_size=60,
    generations=120,
    crossover_rate=0.8,
    mutation_rate=0.1,
    jobs_count=10,
):
    if not jobs:
        jobs = random_jobs(jobs_count, machines=machine_count)

    greedy_results = {}
    greedy_best_name = None
    greedy_best_eval = None
    greedy_best_schedule = []
    greedy_runtime = 0.0

    for policy in ["lpt", "edd", "wspt"]:
        start_policy = time.perf_counter()
        schedule = greedy_schedule(jobs, machine_count, policy=policy)
        eval_result = evaluate_schedule(schedule)
        runtime = time.perf_counter() - start_policy
        greedy_runtime += runtime

        greedy_results[policy] = {
            "objective": eval_result["objective"],
            "makespan": eval_result["makespan"],
            "schedule": serialize_schedule(schedule),
            "runtime": round(runtime, 4),
        }

        if greedy_best_eval is None or eval_result["objective"] < greedy_best_eval["objective"]:
            greedy_best_name = policy
            greedy_best_eval = eval_result
            greedy_best_schedule = schedule

    start_lpt = time.perf_counter()
    lpt_schedule = schedule_lpt(jobs, machine_count)
    lpt_eval = evaluate_schedule(lpt_schedule)
    lpt_time = time.perf_counter() - start_lpt

    start_ga = time.perf_counter()
    ga_result = genetic_algorithm(
        jobs,
        machine_count,
        pop_size=pop_size,
        generations=generations,
        crossover_rate=crossover_rate,
        mutation_rate=mutation_rate,
    )
    ga_eval = evaluate_schedule(ga_result["schedule"])
    ga_time = time.perf_counter() - start_ga

    bb_result = None
    bb_eval = None
    if len(jobs) <= 10:
        start_bb = time.perf_counter()
        bb_result = branch_and_bound(jobs, machine_count)
        bb_eval = evaluate_schedule(bb_result["schedule"]) if bb_result else None
        bb_time = time.perf_counter() - start_bb
    else:
        bb_time = None

    extra_results = {}
    for name, algorithm in (("ts", tabu_search), ("cp_sat", cp_sat)):
        start = time.perf_counter()
        result = algorithm(jobs, machine_count)
        metrics = evaluate_schedule(result["schedule"]) if result["schedule"] is not None else None
        extra_results[name] = {
            **result,
            "objective": metrics["objective"] if metrics else None,
            "makespan": metrics["makespan"] if metrics else None,
            "schedule": serialize_schedule(result["schedule"]) if metrics else None,
            "runtime": round(time.perf_counter() - start, 4),
        }

    return {
        **extra_results,
        "machines": machine_count,
        "jobs": jobs,
        "greedy": {
            "best_policy": greedy_best_name,
            "objective": greedy_best_eval["objective"] if greedy_best_eval else None,
            "makespan": greedy_best_eval["makespan"] if greedy_best_eval else None,
            "schedule": serialize_schedule(greedy_best_schedule),
            "runtime": round(greedy_runtime, 4),
            "policies": greedy_results,
        },
        "lpt": {
            "objective": lpt_eval["objective"],
            "makespan": lpt_eval["makespan"],
            "schedule": serialize_schedule(lpt_schedule),
            "runtime": round(lpt_time, 4),
        },
        "ga": {
            "objective": ga_eval["objective"],
            "makespan": ga_eval["makespan"],
            "schedule": serialize_schedule(ga_result["schedule"]),
            "runtime": round(ga_time, 4),
        },
        "bb": {
            "objective": bb_eval["objective"] if bb_eval else None,
            "makespan": bb_eval["makespan"] if bb_eval else None,
            "schedule": serialize_schedule(bb_result["schedule"]) if bb_result else [],
            "runtime": round(bb_time, 4) if bb_time is not None else None,
            "available": len(jobs) <= 10,
            "status": bb_result["status"] if bb_result else "UNAVAILABLE",
            "optimal": bb_result["optimal"] if bb_result else False,
        },
    }