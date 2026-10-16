import math
import random


DEADLINE_RANGES = {
    "tight": (0.5, 0.9),
    "medium": (0.8, 1.2),
    "wide": (1.2, 1.8),
}


def random_jobs(n, max_processing=20, max_deadline=None, max_weight=5,
                *, machines=3, deadline_level="medium"):
    if machines < 1 or n < 0 or max_processing < 3 or max_weight < 1:
        raise ValueError("Số máy, số việc hoặc khoảng sinh dữ liệu không hợp lệ")
    if deadline_level not in DEADLINE_RANGES:
        raise ValueError("Mức hạn phải là tight, medium hoặc wide")
    jobs = [
        {"id": i + 1, "p": random.randint(3, max_processing),
         "w": random.randint(1, max_weight)}
        for i in range(n)
    ]
    if not jobs:
        return []
    horizon = max(max(job["p"] for job in jobs),
                  sum(job["p"] for job in jobs) / machines)
    low, high = DEADLINE_RANGES[deadline_level]
    for job in jobs:
        # Giờ nguyên trong khoảng tải; mỗi việc có thể đúng hạn nếu chạy ngay.
        lower = max(job["p"], math.ceil(low * horizon))
        upper = max(lower, math.floor(high * horizon))
        # Giữ tham số trần cũ cho người gọi trực tiếp, mặc định không dùng trần.
        if max_deadline is not None:
            if max_deadline < job["p"]:
                raise ValueError("Trần deadline phải không nhỏ hơn thời lượng công việc")
            upper = min(upper, max_deadline)
            lower = min(lower, upper)
        job["d"] = random.randint(lower, upper)
    return jobs
