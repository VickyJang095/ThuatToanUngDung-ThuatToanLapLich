# Tối ưu Lập lịch Đa máy ứng dụng Genetic Algorithm và Trực quan hóa Gantt Chart

Ứng dụng web mô phỏng và so sánh các phương pháp lập lịch đa máy cho bài toán tối ưu hóa trễ hạn có trọng số:

- Greedy (LPT, EDD, WSPT)
- Branch and Bound (B&B)
- Genetic Algorithm (GA)

Ứng dụng hiển thị kết quả dưới dạng Gantt Chart với các công việc được đánh dấu màu xanh nếu đúng hạn và đỏ nếu trễ hạn.

## Mục tiêu bài toán

Cho tập hợp N công việc và M máy song song giống nhau. Mỗi công việc có:

- thời gian thực thi p_i
- deadline d_i
- trọng số ưu tiên w_i

Mục tiêu là tối thiểu hóa hàm mục tiêu:

$$
\sum_{i=1}^{n} w_i \cdot \max(0, C_i - d_i)
$$

với C_i là thời điểm hoàn thành công việc J_i.

## Tính năng chính

- Sinh dữ liệu công việc ngẫu nhiên
- Chọn số máy và số công việc
- Chạy các thuật toán:
  - Greedy
  - B&B (với dữ liệu nhỏ)
  - GA
- So sánh kết quả theo:
  - objective
  - makespan
  - runtime
- Trực quan hóa lịch trình theo Gantt Chart
- Giao diện web tối giản, dễ trình bày và demo

## Công nghệ sử dụng

- Python
- Flask
- HTML/CSS/JavaScript

## Cấu trúc dự án

```text
.
├── app.py
├── requirements.txt
├── README.md
├── scheduling/
│   ├── __init__.py
│   ├── jobs.py
│   ├── metrics.py
│   ├── greedy.py
│   ├── genetic.py
│   ├── branch_and_bound.py
│   └── service.py
├── web/
│   ├── __init__.py
│   └── routes.py
├── static/
│   ├── app.js
│   └── style.css
├── templates/
│   └── index.html
├── tests/
│   └── test_characterization.py
└── .gitignore
```

## Cài đặt

1. Clone project:

```bash
git clone https://github.com/VickyJang095/ThuatToanUngDung-ThuatToanLapLich.git
cd ThuatToanUngDung-ThuatToanLapLich
```

2. Tạo môi trường ảo (khuyến nghị):

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Cài đặt dependencies:

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
python app.py
```

Chạy các kiểm thử bằng thư viện chuẩn của Python:

```bash
python -m unittest discover -s tests -v
```

Mở trình duyệt tại:

```text
http://127.0.0.1:5000
```

## Ví dụ chia sẻ cho teammate test

Nếu muốn truy cập qua máy khác trong cùng mạng nội bộ:

```text
http://10.169.60.15:5000
```

Hoặc dùng ngrok để tạo public URL:

```bash
ngrok http 5000
```

## Thuật toán được tích hợp

### 1. Greedy

Nhóm thuật toán tham lam:

- LPT: xếp công việc có thời gian thực thi dài nhất trước
- EDD: ưu tiên công việc có deadline sớm nhất
- WSPT: ưu tiên công việc có trọng số trên thời gian xử lý cao

Dùng như baseline để so sánh với các thuật toán mạnh hơn.

### 2. Branch and Bound

Dùng cho tối đa 10 công việc. Mã hiện tại duyệt cả thứ tự công việc và cách phân máy, loại bỏ các máy tương đương và cắt nhánh bằng cận dưới. Đã đối chiếu với vét cạn độc lập trên dữ liệu nhỏ.

### 3. Genetic Algorithm

Dùng cho dữ liệu lớn hơn, nâng cao chất lượng lời giải trong thời gian thực tế.

## Tổ chức mã nguồn

- `scheduling/jobs.py`: sinh dữ liệu công việc.
- `scheduling/metrics.py`: tính objective, makespan và thông tin trễ hạn của lịch.
- `scheduling/greedy.py`: các policy LPT, EDD, WSPT; `schedule_lpt()` giữ tên gọi tương thích và dùng chung policy LPT.
- `scheduling/genetic.py`: Genetic Algorithm, giải mã hoán vị và các toán tử di truyền.
- `scheduling/branch_and_bound.py`: thuật toán B&B hiện tại.
- `scheduling/service.py`: điều phối thuật toán, đo runtime và tạo payload kết quả.
- `web/routes.py`: xử lý request Flask cho trang chính và API.
- `app.py`: khởi tạo Flask, đăng ký route và hỗ trợ cách chạy `python app.py`.
- `tests/`: kiểm thử đặc trưng cho thuật toán và schema API.

## Kết luận

Dự án này phù hợp cho mục đích demo và báo cáo môn học vì nó kết hợp:

- lý thuyết lập lịch đa máy
- thuật toán heuristic, exact, metaheuristic
- trực quan hóa dữ liệu bằng Gantt Chart
- khả năng so sánh rõ ràng giữa các phương pháp

## Tác giả

Đề tài được xây dựng phục vụ bài tập lớn và báo cáo môn học về Thuật toán ứng dụng.


## Tabu Search và CP-SAT

- `scheduling/tabu_search.py`: khởi tạo EDD, đổi chỗ hai chỉ số công việc, tabu theo cặp công việc, aspiration và lưu riêng lịch tốt nhất. Mặc định `max_iterations=100`, `tabu_tenure=7`; không có bước hợp lệ thì dừng.
- `scheduling/cp_sat.py`: OR-Tools với optional interval cho từng cặp việc–máy, chọn đúng một máy và NoOverlap. Tối thiểu hóa tổng trễ hạn có trọng số; makespan chỉ để báo cáo. Horizon bằng tổng p vì mọi việc sẵn sàng từ 0 và có thể bỏ thời gian chờ mà không tăng objective.
- CP-SAT yêu cầu p, d, w nguyên (không chấp nhận float kể cả 1.0), p và w không âm; d được phép âm. Thời gian giải mặc định 10 giây.
- API giữ các khóa cũ và thêm `ts`, `cp_sat`. CP-SAT trả `status`, `best_bound`, `optimal`; chỉ OPTIMAL mới có `optimal=true`. Nếu chưa có lịch, objective và schedule là null. Thiếu OR-Tools trả UNAVAILABLE cùng hướng dẫn cài, các thuật toán khác vẫn chạy.
- Giữ hành vi cũ của `run_algorithms`: danh sách jobs rỗng sẽ sinh `jobs_count` công việc; để kiểm tra bài toán rỗng qua service, đặt `jobs_count=0`.

Cài và chạy trên Windows (Python 3.11 đã kiểm tra):

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
# Mở http://127.0.0.1:5000
.venv\Scripts\python.exe -m unittest discover -s tests -v
node tests/test_frontend.cjs
```

Kiểm tra gồm: vét cạn độc lập mọi hoán vị và mọi cách phân máy cho 10 bài toán 1–5 việc; xác minh lịch và objective; TS không kém EDD; tabu/aspiration; rỗng, một việc, thừa máy, p=0, w=0, d âm; kiểm tra kiểu dữ liệu; hết thời gian chưa có lịch; thiếu OR-Tools; JSON API và trạng thái FEASIBLE giả lập. Chưa kiểm tra trực quan trên trình duyệt hoặc hiệu năng dữ liệu lớn.


### Sinh dữ liệu theo tải máy

Backend là nơi duy nhất sinh dữ liệu. Trên giao diện chọn mức hạn rồi bấm **Sinh dữ liệu**; bảng hiển thị đúng bộ dữ liệu dùng khi chạy. Nếu chưa có dữ liệu, nút Chạy gọi API sinh trước.

Giữ p nguyên từ 3–20 giờ, w từ 1–5. Đặt H = max(p lớn nhất, tổng p / số máy). Khoảng deadline: Chặt 0,5H–0,9H; Vừa (mặc định) 0,8H–1,2H; Rộng 1,2H–1,8H. Cận dưới làm tròn lên và ít nhất bằng p của việc; cận trên làm tròn xuống, nâng bằng cận dưới nếu khoảng quá hẹp. Deadline là giờ nguyên tính từ mốc 0. Mức chặt tăng khả năng trễ, không bảo đảm chi phí luôn dương.

API `/api/generate` nhận `machines`, `jobs`, `deadline_level` (`tight`, `medium`, `wide`). Tham số `max_deadline` cho người gọi Python trực tiếp vẫn được hỗ trợ như trần tùy chọn; luồng mặc định không dùng trần 60 giờ nữa.


### Giới hạn chờ khi chạy

B&B dừng sau tối đa 5 giây (tham số Python `time_limit`), trả lịch tốt nhất đã tìm được và `status=TIME_LIMIT`, `optimal=false` nếu hết giờ. Khởi tạo bằng lịch EDD để luôn có lịch khả thi. CP-SAT giữ giới hạn 10 giây. Giao diện báo đang chạy, khóa nút để tránh gửi trùng và hiển thị lỗi API nếu có; phần nhận xét ghi rõ khi B&B hết thời gian.
