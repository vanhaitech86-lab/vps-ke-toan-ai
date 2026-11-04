"""
VPS - KẾ TOÁN AI – Tân Hồng Hà / Tập đoàn VPS
Chạy:  streamlit run app.py
App đứng CẠNH phần mềm FAST: đọc file xuất từ FAST/ngân hàng/hóa đơn điện tử,
xử lý – đối chiếu – cảnh báo, rồi trả file Excel để nhập ngược vào FAST.
"""
import streamlit as st

from core import ai

st.title("VPS - KẾ TOÁN AI")
st.caption("Trợ lý cho Phòng Kế toán – làm việc song song với phần mềm FAST, không thay thế FAST.")

c1, c2, c3 = st.columns(3)
c1.metric("Chức năng", "7 trang")
c2.metric("AI", "Đã bật (" + ai.provider() + ")" if ai.provider() else "Chưa bật")
c3.metric("Nguồn dữ liệu", "File Excel/XML")

st.markdown("""
### Các chức năng (menu bên trái)

| Trang | Làm gì | Đầu vào | Đầu ra |
|---|---|---|---|
| 1. Hóa đơn điện tử XML | Đọc hàng loạt hóa đơn, kiểm tra số học, MST | File XML tải từ cổng hóa đơn điện tử | Excel nhập liệu FAST |
| 2. Đọc chứng từ bằng AI | Ảnh/scan/PDF → dữ liệu | Ảnh chụp, bản scan | Bảng dữ liệu, Excel |
| 3. Đối chiếu ngân hàng | Ghép sao kê với sổ TK 112 | Sao kê NH + sổ tiền gửi FAST | Khớp / lệch |
| 4. Công nợ phải thu | Tuổi nợ, quá hạn, khó đòi | Công nợ chi tiết FAST | Bảng tuổi nợ, danh sách nhắc nợ |
| 5. Tồn kho chậm luân chuyển | Cảnh báo hàng CLC, tồn đọng | Tồn kho + ngày xuất cuối | Danh sách cảnh báo |
| 6. Phân tích BCTC | Chỉ số tài chính + cảnh báo | Số liệu BCĐKT, KQKD | Bảng chỉ số, nhận xét AI |
| 7. Kế hoạch sản phẩm | Thực hiện so với kế hoạch | Kế hoạch & thực hiện | % hoàn thành, nhóm chậm |

**Nguyên tắc:** số liệu do code tính (chính xác, kiểm tra được); AI chỉ đọc chứng từ không có XML và viết nhận xét.
Mọi kết quả phải được kế toán kiểm tra trước khi nhập FAST.
""")
