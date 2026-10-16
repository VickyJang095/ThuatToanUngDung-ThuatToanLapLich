import time

from scheduling.greedy import greedy_schedule
from scheduling.metrics import evaluate_schedule


def branch_and_bound(jobs, machines, time_limit=5.0):
    if len(jobs) > 10:
        return None

    if machines < 1:
        raise ValueError("Số máy phải lớn hơn hoặc bằng 1")

    # Chỉ ưu tiên thứ tự tìm kiếm, không cố định thứ tự xử lý.
    sorted_jobs = sorted(jobs, key=lambda j: (j["d"], j["p"]))

    if time_limit < 0:
        raise ValueError("Giới hạn thời gian phải không âm")
    deadline = time.perf_counter() + time_limit
    # Luôn có lịch khả thi để trả về nếu hết thời gian tìm kiếm.
    best_schedule = greedy_schedule(jobs, machines, policy="edd")
    best_cost = evaluate_schedule(best_schedule)["objective"]
    timed_out = False

    def dfs(remaining, machine_time, schedule, current_cost):
        nonlocal best_cost, best_schedule, timed_out

        if timed_out:
            return
        if time.perf_counter() >= deadline:
            timed_out = True
            return

        if current_cost >= best_cost:
            return

        if not remaining:
            best_cost = current_cost
            best_schedule = [row[:] for row in schedule]
            return

        # Cận dưới: giả sử mỗi việc còn lại đều được bắt đầu
        # tại thời điểm máy rảnh sớm nhất.
        earliest = min(machine_time)
        lower_bound = current_cost + sum(
            max(0, earliest + job["p"] - job["d"]) * job["w"]
            for job in remaining
        )

        if lower_bound >= best_cost:
            return

        # Thử từng công việc chưa xếp.
        for job_index, job in enumerate(remaining):
            next_remaining = (
                remaining[:job_index] + remaining[job_index + 1:]
            )

            # Các máy có cùng thời điểm rảnh là tương đương
            # cho các công việc còn lại, nên chỉ thử một máy.
            tried_times = set()

            for machine_id in sorted(
                range(machines), key=lambda i: (machine_time[i], i)
            ):
                start = machine_time[machine_id]

                if start in tried_times:
                    continue
                tried_times.add(start)

                end = start + job["p"]
                new_cost = (
                    current_cost
                    + max(0, end - job["d"]) * job["w"]
                )

                if new_cost >= best_cost:
                    continue

                # Thử lựa chọn.
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

                dfs(
                    next_remaining,
                    machine_time,
                    schedule,
                    new_cost,
                )

                # Quay lui: khôi phục trước khi thử lựa chọn khác.
                schedule[machine_id].pop()
                machine_time[machine_id] = start

    dfs(
        sorted_jobs,
        [0] * machines,
        [[] for _ in range(machines)],
        0,
    )

    return {
        "objective": best_cost,
        "schedule": best_schedule,
        "status": "TIME_LIMIT" if timed_out else "OPTIMAL",
        "optimal": not timed_out,
    }