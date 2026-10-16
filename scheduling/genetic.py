import random


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
    if n <= 1:
        objective, schedule = decode_permutation(list(range(n)), jobs, machines)
        return {"objective": objective, "schedule": schedule}

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