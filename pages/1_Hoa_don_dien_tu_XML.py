import pandas as pd
import streamlit as st

from core import config as C
from core.einvoice import parse_invoice, to_fast_rows
from core.ui import SAMPLE, download_excel

st.title("1. Hóa đơn điện tử XML → nhập liệu FAST")
st.caption("Tải file XML từ cổng hóa đơn điện tử (hoadondientu.gdt.gov.vn) hoặc email nhà cung cấp. "
           "Đọc trực tiếp XML nên chính xác tuyệt đối, không cần AI.")

files = st.file_uploader("Chọn nhiều file XML", type=["xml"], accept_multiple_files=True)
data = [(f.name, f.read()) for f in files] if files else []
if not data and st.checkbox("Dùng 5 hóa đơn mẫu", value=True):
    data = [(p.name, p.read_bytes()) for p in sorted((SAMPLE / "hoa_don_xml").glob("*.xml"))]

invoices, errors = [], []
for name, b in data:
    try:
        invoices.append(parse_invoice(b, name))
    except Exception as e:
        errors.append(f"{name}: {e}")

if errors:
    st.error("Không đọc được: " + "; ".join(errors))
if invoices:
    head = pd.DataFrame([i.header_dict() for i in invoices])
    bad = head[head["canh_bao"] != ""]
    c1, c2, c3 = st.columns(3)
    c1.metric("Số hóa đơn", len(invoices))
    c2.metric("Tổng thanh toán", f"{head['tong_thanh_toan'].sum():,.0f} đ".replace(",", "."))
    c3.metric("Hóa đơn có cảnh báo", len(bad))
    if len(bad):
        st.warning("Cần kiểm tra trước khi nhập FAST:")
        st.dataframe(bad[["file", "so_hd", "ten_ban", "canh_bao"]], hide_index=True, use_container_width=True)
    st.subheader("Danh sách hóa đơn")
    st.dataframe(head.drop(columns=["file"]), hide_index=True, use_container_width=True)
    fast = pd.DataFrame(to_fast_rows(invoices, C.FAST_IMPORT_COLUMNS))
    st.subheader("Dữ liệu theo mẫu import FAST")
    st.dataframe(fast, hide_index=True, use_container_width=True)
    download_excel({"Import FAST": fast, "Hoa don": head}, "import_FAST_hoa_don.xlsx", "Tải Excel nhập liệu FAST")
    st.caption("Mẫu cột import khai báo ở core/config.py → FAST_IMPORT_COLUMNS; chỉnh cho khớp mẫu import của phiên bản FAST đang dùng.")
