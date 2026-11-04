"""
VPS - KẾ TOÁN AI – chạy:  streamlit run app.py
App đứng CẠNH phần mềm FAST: đọc file xuất từ FAST / ngân hàng / hóa đơn điện tử,
xử lý – đối chiếu – cảnh báo, rồi trả file Excel để nhập ngược vào FAST.
Thêm chức năng mới: tạo file trong pages/ và khai báo 1 dòng st.Page bên dưới.
"""
import streamlit as st

st.set_page_config(page_title="VPS - KẾ TOÁN AI", page_icon="📊", layout="wide")

nav = st.navigation({
    "Tổng quan": [st.Page("pages/0_Trang_chu.py", title="Trang chủ", default=True)],
    "Chứng từ & nhập liệu": [
        st.Page("pages/1_Hoa_don_dien_tu_XML.py", title="1. Hóa đơn điện tử XML"),
        st.Page("pages/2_Doc_chung_tu_bang_AI.py", title="2. Đọc chứng từ bằng AI"),
        st.Page("pages/3_Doi_chieu_ngan_hang.py", title="3. Đối chiếu ngân hàng"),
    ],
    "Phân tích & cảnh báo": [
        st.Page("pages/4_Cong_no_phai_thu.py", title="4. Công nợ phải thu"),
        st.Page("pages/5_Ton_kho_cham_luan_chuyen.py", title="5. Tồn kho chậm luân chuyển"),
        st.Page("pages/6_Phan_tich_BCTC.py", title="6. Phân tích BCTC"),
        st.Page("pages/7_Ke_hoach_san_pham.py", title="7. Kế hoạch sản phẩm"),
    ],
})
nav.run()
