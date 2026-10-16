from numbers import Integral


def cp_sat(jobs, machines, time_limit=10.0):
    if not isinstance(machines, Integral) or isinstance(machines, bool) or machines < 1:
        raise ValueError("Số máy phải là số nguyên dương")
    for job in jobs:
        for field in ("p", "d", "w"):
            value = job[field]
            if isinstance(value, bool) or not isinstance(value, Integral):
                raise ValueError(f"{field} phải là số nguyên, không làm tròn dữ liệu")
            if field in ("p", "w") and value < 0:
                raise ValueError(f"{field} phải không âm")
    if time_limit < 0:
        raise ValueError("Giới hạn thời gian phải không âm")
    # Nạp tùy chọn để thiếu OR-Tools không ảnh hưởng các thuật toán khác.
    try:
        from ortools.sat.python import cp_model
    except ImportError:
        return {"objective": None, "schedule": None, "status": "UNAVAILABLE",
                "best_bound": None, "optimal": False,
                "message": "Thiếu OR-Tools. Cài bằng: pip install -r requirements.txt"}

    model = cp_model.CpModel()
    horizon = sum(job["p"] for job in jobs)
    starts, ends, choices, terms = [], [], [], []
    intervals = [[] for _ in range(machines)]
    for i, job in enumerate(jobs):
        start = model.new_int_var(0, horizon, f"start_{i}")
        end = model.new_int_var(0, horizon, f"end_{i}")
        selected = [model.new_bool_var(f"job_{i}_machine_{m}") for m in range(machines)]
        model.add_exactly_one(selected)
        for m in range(machines):
            intervals[m].append(model.new_optional_interval_var(
                start, job["p"], end, selected[m], f"interval_{i}_{m}"))
        tardiness = model.new_int_var(0, max(0, horizon - job["d"]), f"tardiness_{i}")
        model.add_max_equality(tardiness, [0, end - job["d"]])
        terms.append(job["w"] * tardiness)
        starts.append(start)
        ends.append(end)
        choices.append(selected)
    for row in intervals:
        model.add_no_overlap(row)
    model.minimize(sum(terms))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    status = solver.solve(model)
    result = {"objective": None, "schedule": None, "status": solver.status_name(status),
              "best_bound": solver.best_objective_bound, "optimal": status == cp_model.OPTIMAL}
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return result
    schedule = [[] for _ in range(machines)]
    for i, job in enumerate(jobs):
        m = next(m for m in range(machines) if solver.value(choices[i][m]))
        schedule[m].append({**job, "start": solver.value(starts[i]),
                            "end": solver.value(ends[i]), "machine": m + 1})
    for row in schedule:
        row.sort(key=lambda task: (task["start"], task["end"]))
    # Tính bằng số nguyên từ lịch để tránh sai số biểu diễn float.
    result.update(objective=sum(t["w"] * max(0, t["end"] - t["d"])
                                for row in schedule for t in row), schedule=schedule)
    return result
