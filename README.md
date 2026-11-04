# VPS - KẾ TOÁN AI – khung app cho Phòng Kế toán

App web nội bộ chạy **song song với phần mềm FAST**. Nó không thay FAST: nó nhận các file
anh/chị đang có (XML hóa đơn, sao kê ngân hàng, báo cáo xuất từ FAST), rồi tự đọc, đối chiếu
và cảnh báo. Kết quả trả ra là file Excel để nhập ngược vào FAST hoặc gửi lãnh đạo.

## 7 chức năng có sẵn

| # | Trang | Yêu cầu của Phòng Kế toán được đáp ứng |
|---|---|---|
| 1 | Hóa đơn điện tử XML | Đọc hóa đơn và nhập liệu |
| 2 | Đọc chứng từ bằng AI | Trích xuất dữ liệu từ ảnh, bản scan |
| 3 | Đối chiếu ngân hàng | Đối chiếu ngân hàng |
| 4 | Công nợ phải thu | Đối chiếu công nợ, phân tích công nợ quá hạn, khó đòi |
| 5 | Tồn kho chậm luân chuyển | Phân tích tồn kho, cảnh báo hàng CLC |
| 6 | Phân tích BCTC | Phân tích BCTC, chỉ số tài chính, cảnh báo số liệu |
| 7 | Kế hoạch sản phẩm | Phân tích việc thực hiện kế hoạch sản phẩm |

Các con số đều do code tính, nên chính xác và kiểm tra lại được. AI chỉ làm hai việc: đọc
chứng từ không có XML, và viết nhận xét, cảnh báo dựa trên bảng kết quả.

## Cài đặt (Windows, khoảng 10 phút)

1. Cài **Python 3.11 trở lên** từ python.org. Khi cài, tick ô "Add Python to PATH".
2. Giải nén thư mục `VPS - KẾ TOÁN AI`, mở **Command Prompt** tại thư mục đó.
3. Cài thư viện:
   ```
   pip install -r requirements.txt
   ```
4. Tạo dữ liệu mẫu để chạy thử:
   ```
   python tao_du_lieu_mau.py
   ```
5. Chạy app:
   ```
   streamlit run app.py
   ```
   Trình duyệt sẽ mở địa chỉ http://localhost:8501.

**Bật AI (không bắt buộc):** đổi tên `.env.example` thành `.env`, rồi điền `GEMINI_API_KEY`
(lấy tại Google AI Studio) hoặc `OPENAI_API_KEY`. Không có khóa thì trang 1, 3, 4, 5, 6, 7
vẫn chạy đầy đủ, chỉ tắt phần nhận xét AI và trang 2.

**Cho cả phòng dùng chung:** chạy app trên một máy trong mạng nội bộ bằng lệnh
`streamlit run app.py --server.address 0.0.0.0`. Máy khác mở `http://<IP máy đó>:8501`.

## Bước quan trọng nhất: khớp tên cột với file FAST

Mở file `core/config.py`. Mỗi chức năng đọc Excel **theo tên cột**. Làm 3 bước sau:

1. Xuất từ FAST các báo cáo: sổ tiền gửi ngân hàng (TK 112), công nợ chi tiết theo hóa đơn
   (TK 131), tồn kho kèm ngày xuất cuối.
2. Xem tên cột thật trong các file đó và sửa phần bên phải dấu `:` trong `config.py`.
   Ví dụ đổi `"ngay": "Ngày CT"` thành `"ngay": "Ngày chứng từ"`.
3. Lấy mẫu file import chứng từ của FAST, sửa `FAST_IMPORT_COLUMNS` cho đúng thứ tự cột.

Nếu tải lên file thiếu cột, app sẽ báo rõ thiếu cột nào và liệt kê các cột đang có.

## Cấu trúc thư mục

```
VPS - KẾ TOÁN AI/
├── app.py                  # menu & điều hướng
├── pages/                  # mỗi chức năng 1 file
├── core/
│   ├── config.py           # ← sửa tên cột, ngưỡng cảnh báo tại đây
│   ├── einvoice.py         # đọc XML hóa đơn theo TT78
│   ├── analysis.py         # đối chiếu NH, tuổi nợ, tồn kho, chỉ số, kế hoạch
│   ├── ai.py               # kết nối Gemini / OpenAI
│   └── ui.py               # thành phần giao diện dùng chung
├── tao_du_lieu_mau.py      # sinh dữ liệu thử
├── tests/test_core.py      # kiểm thử: python -m pytest -q
└── requirements.txt
```

## Thêm chức năng mới

1. Tạo file mới trong `pages/`, ví dụ `8_Doi_chieu_cong_no_NCC.py`.
2. Thêm một dòng `st.Page(...)` vào `app.py`.
3. Phép tính đặt trong `core/analysis.py`, để có thể kiểm thử riêng.

Mẹo: đưa file `README.md`, `config.py` và một file trang có sẵn cho ChatGPT, Gemini hoặc
Claude, rồi yêu cầu *"viết thêm trang … theo đúng cấu trúc này"*.

## Lộ trình gợi ý

| Giai đoạn | Việc |
|---|---|
| Tuần 1–2 | Chạy với dữ liệu mẫu → khớp tên cột với file FAST thật → dùng trang 1, 3, 4 hằng ngày |
| Tuần 3–4 | Bật AI, dùng trang 2 cho chứng từ giấy; thêm nhận xét AI cho báo cáo tuần |
| Tháng 2 | Thêm đối chiếu công nợ nhà cung cấp, mẫu thư nhắc nợ tự động gửi email/Zalo |
| Tháng 3+ | Khi CRM ↔ FAST đã đồng bộ: đọc dữ liệu trực tiếp (không cần tải file), lên dashboard |

## Lưu ý an toàn

- File dữ liệu chỉ nằm trên máy chạy app; chỉ phần gửi cho AI mới ra ngoài.
- Chỉ dùng khóa API hoặc tài khoản AI bản doanh nghiệp. Không đưa file `.env` cho người khác.
- Mọi kết quả phải được kế toán rà soát trước khi nhập FAST hoặc gửi khách hàng.
