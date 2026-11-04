from datetime import date

import streamlit as st

from core import config as C
from core.analysis import slow_moving
from core.ui import ai_comment, check_columns, download_excel, load_excel, short

st.title("5. Tồn kho – cảnh báo hàng chậm luân chuyển")
st.caption(f"Chậm luân chuyển: không xuất > {C.SLOW_MOVING_DAYS} ngày · Tồn đọng: > {C.DEAD_STOCK_DAYS} ngày (sửa ngưỡng trong core/config.py).")
df = load_excel("Báo cáo tồn kho kèm ngày xuất cuối (xuất từ FAST)", "ton_kho.xlsx", "inv")

if df is not None and check_columns(df, C.INV_COLUMNS, "tồn kho"):
    d = slow_moving(df, date.today())
    warn = d[d["tinh_trang"] != "Bình thường"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng giá trị tồn", short(d["gt_ton"].sum()))
    c2.metric("Giá trị hàng cần xử lý", short(warn["gt_ton"].sum()), f"{len(warn)} mã", delta_color="inverse")
    c3.metric("Tỷ trọng", f"{warn['gt_ton'].sum() / d['gt_ton'].sum():.0%}" if d["gt_ton"].sum() else "–")
    st.bar_chart(d.groupby("tinh_trang")["gt_ton"].sum())
    st.subheader("Danh sách cảnh báo")
    st.dataframe(warn, hide_index=True, use_container_width=True)
    download_excel({"Canh bao ton kho": warn, "Toan bo": d}, "canh_bao_ton_kho.xlsx")
    ai_comment("Hàng tồn kho chậm luân chuyển", warn,
               "Đề xuất hướng xử lý: khuyến mãi, chuyển kho, trả NCC, trích lập dự phòng giảm giá hàng tồn kho.", key="ai_inv")
