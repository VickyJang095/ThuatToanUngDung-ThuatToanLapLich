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


def schedule_lpt(jobs, machines):
    return greedy_schedule(jobs, machines, policy="lpt")