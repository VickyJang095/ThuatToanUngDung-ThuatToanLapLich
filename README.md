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
├── static/
│   ├── app.js
│   └── style.css
├── templates/
│   └── index.html
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
Dùng cho dữ liệu nhỏ, đảm bảo tìm lời giải tối ưu tuyệt đối.

### 3. Genetic Algorithm
Dùng cho dữ liệu lớn hơn, nâng cao chất lượng lời giải trong thời gian thực tế.

## Kết luận

Dự án này phù hợp cho mục đích demo và báo cáo môn học vì nó kết hợp:

- lý thuyết lập lịch đa máy
- thuật toán heuristic, exact, metaheuristic
- trực quan hóa dữ liệu bằng Gantt Chart
- khả năng so sánh rõ ràng giữa các phương pháp

## Tác giả

Đề tài được xây dựng phục vụ bài tập lớn và báo cáo môn học về Thuật toán ứng dụng.
