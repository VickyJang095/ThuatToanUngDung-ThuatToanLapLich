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