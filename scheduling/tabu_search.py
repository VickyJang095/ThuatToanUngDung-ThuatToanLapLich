from scheduling.genetic import decode_permutation


def tabu_search(jobs, machines, max_iterations=100, tabu_tenure=7):
    if machines < 1:
        raise ValueError("Số máy phải lớn hơn hoặc bằng 1")
    if max_iterations < 0 or tabu_tenure < 0:
        raise ValueError("Số vòng và tabu tenure phải không âm")
    current = sorted(range(len(jobs)), key=lambda i: jobs[i]["d"])
    best_obj, best_schedule = decode_permutation(current, jobs, machines)
    tabu_until = {}
    for iteration in range(max_iterations):
        candidate = None
        for i in range(len(current)):
            for j in range(i + 1, len(current)):
                move = tuple(sorted((current[i], current[j])))
                neighbor = current[:]
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                objective, schedule = decode_permutation(neighbor, jobs, machines)
                # Vượt tabu khi cải thiện tốt nhất toàn cục.
                if tabu_until.get(move, -1) > iteration and objective >= best_obj:
                    continue
                if candidate is None or objective < candidate[0]:
                    candidate = (objective, neighbor, schedule, move)
        # Không có bước hợp lệ: dừng và trả lời giải tốt nhất đã lưu.
        if candidate is None:
            break
        objective, current, schedule, move = candidate
        tabu_until = {key: expiry for key, expiry in tabu_until.items() if expiry > iteration}
        tabu_until[move] = iteration + tabu_tenure + 1
        if objective < best_obj:
            best_obj, best_schedule = objective, schedule
    return {"objective": best_obj, "schedule": best_schedule}
