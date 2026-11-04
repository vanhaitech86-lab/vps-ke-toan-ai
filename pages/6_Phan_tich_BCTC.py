import pandas as pd
import streamlit as st

from core.analysis import RATIO_INPUTS, financial_ratios
from core.ui import ai_comment, download_excel

st.title("6. Phân tích báo cáo tài chính & cảnh báo chỉ số")
st.caption("Nhập số liệu từ Bảng cân đối kế toán và Báo cáo kết quả kinh doanh (đơn vị: triệu đồng). "
           "Số mặc định là ví dụ – thay bằng số thật của kỳ.")

defaults = dict(tai_san_ngan_han=58_000, hang_ton_kho=21_000, phai_thu=19_500, tong_tai_san=82_000, no_ngan_han=46_000,
                tong_no=55_000, von_chu_so_huu=27_000, doanh_thu=120_000, gia_von=98_000, loi_nhuan_sau_thue=3_100)
cols = st.columns(2)
v = {}
for n, (k, label) in enumerate(RATIO_INPUTS):
    v[k] = cols[n % 2].number_input(label, value=float(defaults[k]), step=100.0, format="%.0f")

r = financial_ratios(v)
show = r.copy()
show["Giá trị"] = [("–" if x is None else (f"{x:.1%}" if u == "%" else f"{x:,.2f}")) for x, u in zip(r["Giá trị"], r["Đơn vị"])]
st.subheader("Chỉ số tài chính")
st.dataframe(show, hide_index=True, use_container_width=True)
flags = r[r["Đánh giá"] == "Cảnh báo"]
if len(flags):
    st.error("Cảnh báo: " + ", ".join(flags["Chỉ số"]))
download_excel({"Chi so": show, "So lieu": pd.DataFrame([{l: v[k] for k, l in RATIO_INPUTS}])}, "chi_so_tai_chinh.xlsx")
ai_comment("Chỉ số tài chính kỳ này", show,
           "Đánh giá thanh khoản, đòn bẩy, hiệu quả; nêu rủi ro và 3 việc Ban Giám đốc nên làm.", key="ai_fin")
