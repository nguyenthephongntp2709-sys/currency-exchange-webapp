# Currency Exchange - Hệ Thống Chuyển Đổi & Theo Dõi Tỷ Giá Hối Đoái

Dự án ứng dụng web chuyển đổi tiền tệ và phân tích xu hướng tỷ giá được phát triển bằng **Python (Flask)**, kết hợp với cơ sở dữ liệu **SQLite**, thư viện biểu đồ **Chart.js**, và tích hợp API tỷ giá quốc tế cùng dữ liệu tỷ giá niêm yết theo thời gian thực từ Ngân hàng Ngoại thương Việt Nam (Vietcombank).

---

## Mục Lục
1. [Giới Thiệu Dự Án](#giới-thiệu-dự-án)
2. [Các Tính Năng Chính](#các-tính-năng-chính)
3. [Phân Tích Thư Viện (requirements.txt)](#phân-tích-thư-viện-requirementstxt)
4. [Cấu Trúc Thư Mục](#cấu-trúc-thư-mục)
5. [Hướng Dẫn Cài Đặt](#hướng-dẫn-cài-đặt)
   - [Yêu cầu tiên quyết](#yêu-cầu-tiên-quyết)
   - [Tạo và kích hoạt môi trường ảo](#tạo-và-kích-hoạt-môi-trường-ảo)
   - [Cài đặt thư viện dependencies](#cài-đặt-thư-viện-dependencies)
6. [Cấu Hình Cơ Sở Dữ Liệu](#cấu-hình-cơ-sở-dữ-liệu)
7. [Khởi Chạy Ứng Dụng](#khởi-chạy-ứng-dụng)
8. [Chạy Kiểm Thử (Unit Test)](#chạy-kiểm-thử-unit-test)

---

## Giới Thiệu Dự Án

**Currency Exchange** là công cụ giúp người dùng tra cứu tỷ giá tức thời, thực hiện quy đổi giữa nhiều loại tiền tệ khác nhau và theo dõi biến động tỷ giá theo biểu đồ trực quan. 

Điểm nổi bật của hệ thống là cung cấp 2 nguồn dữ liệu tỷ giá linh hoạt:
- **Frankfurter API**: Hệ thống dữ liệu tỷ giá quốc tế mã nguồn mở, hỗ trợ đa dạng cặp tiền tệ phổ biến trên thế giới.
- **Vietcombank XML Portal**: Cập nhật trực tiếp bảng tỷ giá niêm yết chính thức từ cổng thông tin Ngân hàng Vietcombank (hỗ trợ phân loại chi tiết: Mua tiền mặt, Mua chuyển khoản, Bán ngoại tệ).

---

## Các Tính Năng Chính

1. **Quy đổi tiền tệ đa nguồn:**
   - Hỗ trợ đổi chiều tiền tệ nhanh (`⇄ Swap`).
   - Tự động thay đổi tùy chọn giao dịch theo nguồn: khi chọn **Vietcombank**, hệ thống tự động lọc danh sách tiền tệ hỗ trợ và đưa ra lựa chọn loại giao dịch phù hợp (*Mua tiền mặt*, *Mua chuyển khoản* hoặc *Bán*).
2. **Lưu vết lịch sử giao dịch (Conversion History):**
   - Mọi lượt tính toán, quy đổi của người dùng đều được lưu tự động vào database để đối soát và tra cứu lại.
3. **Biểu đồ xu hướng tỷ giá (Rate History Chart):**
   - Trực quan hóa biến động tỷ giá (mặc định cặp USD/VND) bằng **Chart.js**.
   - Hỗ trợ chuyển đổi nhanh các mốc thời gian: **7 ngày**, **1 tháng**, **1 năm**.
4. **Cơ chế tự động khởi tạo và nạp dữ liệu mẫu (Auto Seeding):**
   - Ứng dụng tự kiểm tra và khởi tạo bảng trong SQLite khi khởi động lần đầu, đồng thời sinh dữ liệu mô phỏng 365 ngày cho biểu đồ nếu database đang trống.

---

## Phân Tích Thư Viện (requirements.txt)

Tệp `requirements.txt` của dự án được trích xuất từ môi trường phát triển đầy đủ. Cụ thể có thể chia thành 2 nhóm thư viện:

### 1. Nhóm thư viện cốt lõi vận hành ứng dụng (Production Core)
- **`Flask==3.1.3`**: Web framework chính để định tuyến URL (Routing), quản lý Blueprint (`currency_bp`, `history_bp`), và xử lý HTTP Request/Response.
- **`requests==2.34.2`**: Thư viện HTTP client gửi request lấy dữ liệu từ Frankfurter API và tải tệp XML tỷ giá từ máy chủ Vietcombank.
- **`Jinja2==3.1.6` & `MarkupSafe==3.0.3`**: Template Engine kết xuất giao diện HTML động, hỗ trợ hiển thị dữ liệu bảng và form.
- **`Werkzeug==3.1.9`**: Bộ công cụ WSGI nền tảng của Flask, xử lý server dev và context.
- **`click==8.5.0` & `blinker==1.9.0` & `itsdangerous==2.2.0`**: Các package bổ trợ trực tiếp của hệ sinh thái Flask.
- *Lưu ý về thư viện chuẩn:* Cơ sở dữ liệu sử dụng module tích hợp sẵn `sqlite3`, và phân tích cú pháp XML dùng `xml.etree.ElementTree`, do đó không cần cài thêm driver ngoài.

### 2. Nhóm thư viện công cụ & Môi trường Notebook (Dev/Data Science)
- **`jupyterlab`, `notebook`, `ipykernel`, `ipython`**: Các gói hỗ trợ chạy Jupyter Notebook trong quá trình nghiên cứu, thử nghiệm thuật toán và trích xuất dữ liệu.
- **`beautifulsoup4`, `soupsieve`**: Phục vụ bóc tách dữ liệu web HTML/XML phục vụ phân tích.
- **`tornado`, `pyzmq`, `anyio`, `traitlets`, `jsonschema`...**: Các dependencies nền tảng đi kèm phục vụ môi trường máy chủ của Jupyter và IPython.

> **Mẹo:** Để triển khai gọn nhẹ (lightweight), môi trường chỉ cần cài đặt `Flask` và `requests`. Tuy nhiên, để đảm bảo tính tương thích toàn diện với môi trường sẵn có của dự án, bạn nên cài đặt toàn bộ theo hướng dẫn bên dưới.

---

## Cấu Trúc Thư Mục

```text
├── database/
│   ├── __init__.py
│   └── database.py              # Xử lý kết nối SQLite, CRUD lịch sử và hàm nạp seed data
├── routes/
│   ├── __init__.py
│   ├── currency_routes.py       # Tuyến đường xử lý trang chủ "/" và tính toán quy đổi
│   └── history_routes.py        # Tuyến đường "/history" và API biểu đồ "/api/rate-history/<pair>"
├── services/
│   ├── exchange_api.py          # Kết nối Frankfurter API (tỷ giá quốc tế)
│   └── vietcombank_service.py   # Lấy & phân tích XML tỷ giá Vietcombank
├── static/
│   ├── css/
│   │   └── style.css            # Giao diện responsive hiện đại
│   └── js/
│       ├── chart.js             # File script biểu đồ bổ sung
│       └── main.js              # Xử lý tương tác động form, dropdown và đảo cặp tiền tệ
├── templates/
│   ├── history.html             # Giao diện trang xem biểu đồ và lịch sử quy đổi
│   └── index.html               # Giao diện chính quy đổi tiền tệ
├── tests/
│   ├── __init__.py
│   └── test_database.py         # Kiểm thử đơn vị cho tầng Database
├── .gitignore                   # Quy tắc bỏ qua file rác, file *.db và venv
├── requirements.txt             # Danh sách dependencies của dự án
└── webapp.py                    # Điểm khởi chạy chính của ứng dụng Flask
```

---

## Hướng Dẫn Cài Đặt

### Yêu cầu tiên quyết
- **Python**: Phiên bản `3.10` trở lên (Khuyến nghị `Python 3.11` hoặc `3.12`).
- Quản lý gói: **`pip`** cập nhật mới nhất.
- Đảm bảo máy tính có kết nối Internet để tải packages và lấy dữ liệu tỷ giá trực tuyến.

---

### Bước 1: Chuẩn bị mã nguồn
Mở cửa sổ dòng lệnh (Terminal / Command Prompt / PowerShell) và điều hướng đến thư mục dự án:
```bash
cd duong/dan/toi/du-an
```

---

### Bước 2: Tạo và kích hoạt môi trường ảo (Virtual Environment)

Khởi tạo một môi trường ảo tên là `.venv` hoặc `venv` để tránh xung đột thư viện hệ thống:

* **Trên Windows (Command Prompt / PowerShell):**
  ```cmd
  # Khởi tạo môi trường ảo
  python -m venv venv

  # Kích hoạt trên Command Prompt (cmd)
  venv\Scripts\activate

  # Hoặc kích hoạt trên PowerShell:
  venv\Scripts\Activate.ps1
  ```
  *(Lưu ý: Nếu PowerShell báo lỗi Execution Policy, chạy lệnh: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*

* **Trên macOS / Linux:**
  ```bash
  # Khởi tạo môi trường ảo
  python3 -m venv venv

  # Kích hoạt
  source venv/bin/activate
  ```

Sau khi kích hoạt thành công, bạn sẽ thấy tiền tố `(venv)` xuất hiện ở đầu dòng lệnh.

---

### Bước 3: Cài đặt Dependencies

Nâng cấp công cụ `pip` lên bản mới nhất:
```bash
python -m pip install --upgrade pip
```

Cài đặt tất cả thư viện theo file `requirements.txt`:
```bash
pip install -r requirements.txt
```

> **Cách thay thế (Cài đặt tối giản):** Nếu bạn chỉ muốn chạy ứng dụng web mà không cần các công cụ Jupyter/Data Science:
> ```bash
> pip install Flask requests
> ```

---

## Cấu Hình Cơ Sở Dữ Liệu

Dự án sử dụng cơ sở dữ liệu **SQLite** cục bộ (tệp `exchange.db`). Bạn **không cần phải cài đặt máy chủ cơ sở dữ liệu riêng biệt** (như MySQL hay PostgreSQL).

### Cơ chế tự động khởi tạo:
Trong file `webapp.py`, hệ thống đã cấu hình 2 hàm chạy tự động mỗi khi server khởi động:
1. `init_db()`: Tự động tạo tệp `exchange.db` (nếu chưa có) và khởi tạo 2 bảng dữ liệu:
   - `conversion_history`: Lưu lại lịch sử các giao dịch quy đổi (thời gian, tiền nguồn, tiền đích, số tiền, tỷ giá, kết quả).
   - `exchange_rate_history`: Lưu lịch sử tỷ giá theo ngày để hiển thị biểu đồ xu hướng.
2. `seed_rate_history()`: Tự động kiểm tra bảng `exchange_rate_history`. Nếu chưa có dữ liệu, hàm sẽ tự động tạo sẵn 365 bản ghi lịch sử tỷ giá USD/VND mẫu để biểu đồ có thể vẽ ngay mà không cần đợi nạp thủ công.

---

## Khởi Chạy Ứng Dụng

Sau khi hoàn tất cài đặt môi trường và dependencies, chạy lệnh sau tại thư mục gốc của dự án:

```bash
python webapp.py
```

Khi ứng dụng khởi động thành công, màn hình terminal sẽ thông báo:
```text
 * Serving Flask app 'webapp'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

Mở trình duyệt web bất kỳ và truy cập vào địa chỉ:
- **Trang chuyển đổi tỷ giá:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **Trang lịch sử & biểu đồ:** [http://127.0.0.1:5000/history](http://127.0.0.1:5000/history)

---
