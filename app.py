from flask import Flask, render_template, request, jsonify
import random
import time

app = Flask(__name__)


def random_jobs(n, max_processing=20, max_deadline=60, max_weight=5):
    jobs = []
    for i in range(1, n + 1):
        p = random.randint(3, max_processing)
        deadline = random.randint(max(8, p + 4), max_deadline)
        weight = random.randint(1, max_weight)
        jobs.append({"id": i, "p": p, "d": deadline, "w": weight})
    return jobs


def schedule_lpt(jobs, machines):
    ordered = sorted(jobs, key=lambda j: (j["p"], j["d"]), reverse=True)
    machine_time = [0] * machines
    schedule = [[] for _ in range(machines)]

    for job in ordered:
        machine_id = min(range(machines), key=lambda i: (machine_time[i], i))
        start = machine_time[machine_id]
        end = start + job["p"]
        machine_time[machine_id] = end
        schedule[machine_id].append({
            "id": job["id"],
            "start": start,
            "end": end,
            "p": job["p"],
            "d": job["d"],
            "w": job["w"],
            "machine": machine_id + 1,
        })

    return schedule


def greedy_schedule(jobs, machines, policy="lpt"):
    if policy == "edd":
        ordered = sorted(jobs, key=lambda j: (j["d"], j["p"]))
    elif policy == "wspt":
        ordered = sorted(jobs, key=lambda j: (j["w"] / max(j["p"], 1), j["d"]), reverse=True)
    else:
        ordered = sorted(jobs, key=lambda j: (j["p"], j["d"]), reverse=True)

    machine_time = [0] * machines
    schedule = [[] for _ in range(machines)]

    for job in ordered:
        machine_id = min(range(machines), key=lambda i: (machine_time[i], i))
        start = machine_time[machine_id]
        end = start + job["p"]
        machine_time[machine_id] = end
        schedule[machine_id].append({
            "id": job["id"],
            "start": start,
            "end": end,
            "p": job["p"],
            "d": job["d"],
            "w": job["w"],
            "machine": machine_id + 1,
        })

    return schedule


def evaluate_schedule(schedule):
    total = 0
    jobs = []
    for machine_jobs in schedule:
        for job in machine_jobs:
            tardiness = max(0, job["end"] - job["d"])
            total += job["w"] * tardiness
            jobs.append({
                "id": job["id"],
                "machine": job["machine"],
                "start": job["start"],
                "end": job["end"],
                "d": job["d"],
                "w": job["w"],
                "tardy": tardiness > 0,
                "tardiness": tardiness,
            })
    makespan = max((job["end"] for machine_jobs in schedule for job in machine_jobs), default=0)
    return {"objective": total, "makespan": makespan, "jobs": jobs}


def decode_permutation(perm, jobs, machines):
    machine_time = [0] * machines
    schedule = [[] for _ in range(machines)]
    total = 0

    for job_index in perm:
        job = jobs[job_index]
        machine_id = min(range(machines), key=lambda i: (machine_time[i], i))
        start = machine_time[machine_id]
        end = start + job["p"]
        machine_time[machine_id] = end
        task = {
            "id": job["id"],
            "start": start,
            "end": end,
            "p": job["p"],
            "d": job["d"],
            "w": job["w"],
            "machine": machine_id + 1,
        }
        schedule[machine_id].append(task)
        total += max(0, end - job["d"]) * job["w"]

    return total, schedule


def random_permutation(n):
    arr = list(range(n))
    random.shuffle(arr)
    return arr


def crossover(parent1, parent2):
    n = len(parent1)
    child = [-1] * n
    start, end = sorted(random.sample(range(n), 2))

    for i in range(start, end + 1):
        child[i] = parent1[i]

    remaining = [v for v in parent2 if v not in child]
    j = 0
    for i in range(n):
        if child[i] == -1:
            child[i] = remaining[j]
            j += 1
    return child


def mutate(chromosome):
    if len(chromosome) < 2:
        return chromosome
    idx1, idx2 = random.sample(range(len(chromosome)), 2)
    chromosome[idx1], chromosome[idx2] = chromosome[idx2], chromosome[idx1]
    return chromosome


def genetic_algorithm(jobs, machines, pop_size=60, generations=120, crossover_rate=0.8, mutation_rate=0.1):
    n = len(jobs)
    if n == 0:
        return {"objective": 0, "schedule": [[] for _ in range(machines)]}

    population = [random_permutation(n) for _ in range(pop_size)]
    best_obj = float("inf")
    best_schedule = []

    for _ in range(generations):
        scored = []
        for chromosome in population:
            obj, schedule = decode_permutation(chromosome, jobs, machines)
            scored.append((obj, chromosome, schedule))

        scored.sort(key=lambda x: x[0])
        best_obj = scored[0][0]
        best_schedule = scored[0][2]

        elite_count = max(2, pop_size // 10)
        next_population = [scored[i][1] for i in range(elite_count)]

        while len(next_population) < pop_size:
            if random.random() < crossover_rate:
                parent1 = random.choice(scored[:max(5, pop_size // 4)])[1]
                parent2 = random.choice(scored[:max(5, pop_size // 4)])[1]
                child1 = crossover(parent1, parent2)
                child2 = crossover(parent2, parent1)
                if random.random() < mutation_rate:
                    mutate(child1)
                if random.random() < mutation_rate:
                    mutate(child2)
                next_population.extend([child1, child2])
            else:
                next_population.append(random_permutation(n))

        population = next_population[:pop_size]

    return {"objective": best_obj, "schedule": best_schedule}


def branch_and_bound(jobs, machines):
    if len(jobs) > 10:
        return None

    sorted_jobs = sorted(jobs, key=lambda j: (j["d"], j["p"]), reverse=True)
    best_cost = float("inf")
    best_schedule = None

    def dfs(index, machine_time, schedule, current_cost):
        nonlocal best_cost, best_schedule

        if index == len(sorted_jobs):
            if current_cost < best_cost:
                best_cost = current_cost
                best_schedule = [list(machine) for machine in schedule]
            return

        if current_cost >= best_cost:
            return

        job = sorted_jobs[index]
        for machine_id in range(machines):
            start = machine_time[machine_id]
            end = start + job["p"]
            new_machine_time = machine_time[:]
            new_machine_time[machine_id] = end

            new_schedule = [row[:] for row in schedule]
            new_schedule[machine_id].append({
                "id": job["id"],
                "start": start,
                "end": end,
                "p": job["p"],
                "d": job["d"],
                "w": job["w"],
                "machine": machine_id + 1,
            })

            new_cost = current_cost + max(0, end - job["d"]) * job["w"]
            dfs(index + 1, new_machine_time, new_schedule, new_cost)

    dfs(0, [0] * machines, [[] for _ in range(machines)], 0)

    if best_schedule is None:
        return {"objective": 0, "schedule": [[] for _ in range(machines)]}

    return {"objective": best_cost, "schedule": best_schedule}


def serialize_schedule(schedule):
    return [{
        "machine": i + 1,
        "jobs": jobs,
    } for i, jobs in enumerate(schedule)]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def generate_jobs_api():
    data = request.get_json(force=True)
    machine_count = int(data.get("machines", 3))
    job_count = int(data.get("jobs", 10))
    jobs = random_jobs(job_count)
    return jsonify({"machines": machine_count, "jobs": jobs})


@app.route("/api/run", methods=["POST"])
def run_algorithms():
    data = request.get_json(force=True)
    machine_count = int(data.get("machines", 3))
    jobs = data.get("jobs", [])
    pop_size = int(data.get("population", 60))
    generations = int(data.get("generations", 120))
    crossover_rate = float(data.get("crossover", 0.8))
    mutation_rate = float(data.get("mutation", 0.1))

    if not jobs:
        jobs = random_jobs(int(data.get("jobs_count", 10)))

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
    ga_result = genetic_algorithm(jobs, machine_count, pop_size=pop_size, generations=generations,
                                 crossover_rate=crossover_rate, mutation_rate=mutation_rate)
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

    response = {
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
        },
    }
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
