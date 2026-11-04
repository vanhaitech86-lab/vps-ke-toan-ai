from datetime import date

import streamlit as st

from core import config as C
from core.analysis import ar_aging, ar_summary
from core.ui import ai_comment, check_columns, download_excel, load_excel, short

st.title("4. Công nợ phải thu – tuổi nợ, quá hạn, khó đòi")
df = load_excel("Công nợ chi tiết theo hóa đơn (xuất từ FAST)", "cong_no_phai_thu.xlsx", "ar")
as_of = st.date_input("Tính đến ngày", date.today(), format="DD/MM/YYYY")

if df is not None and check_columns(df, {k: v for k, v in C.AR_COLUMNS.items() if k in ("ma_kh", "ten_kh", "ngay_hd", "phai_thu")}, "công nợ"):
    aged = ar_aging(df, as_of)
    summ = ar_summary(aged)
    over = aged[aged["so_ngay_qua_han"] > 0]
    bad = aged[aged["so_ngay_qua_han"] > 90]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tổng còn phải thu", short(aged["con_no"].sum()))
    c2.metric("Quá hạn", short(over["con_no"].sum()), f"{len(over)} hóa đơn", delta_color="inverse")
    c3.metric("Khó đòi (> 90 ngày)", short(bad["con_no"].sum()), f"{len(bad)} hóa đơn", delta_color="inverse")
    c4.metric("Tỷ lệ quá hạn", f"{over['con_no'].sum() / aged['con_no'].sum():.0%}" if len(aged) else "–")

    st.subheader("Cơ cấu tuổi nợ")
    order = [b[1] for b in C.AR_BUCKETS]
    st.bar_chart(aged.groupby("nhom_tuoi_no")["con_no"].sum().reindex(order).fillna(0), sort=False)
    st.subheader("Tuổi nợ theo khách hàng (sắp theo số quá hạn)")
    st.dataframe(summ, hide_index=True, use_container_width=True)
    st.subheader("Danh sách nhắc nợ")
    cols = [c for c in ["ma_kh", "ten_kh", "so_hd", "ngay_hd", "han_tt", "con_no", "so_ngay_qua_han", "nhom_tuoi_no", "nv_kd"] if c in aged]
    remind = over.sort_values("so_ngay_qua_han", ascending=False)[cols]
    st.dataframe(remind, hide_index=True, use_container_width=True)
    download_excel({"Tuoi no KH": summ, "Nhac no": remind}, "tuoi_no_phai_thu.xlsx")
    ai_comment("Tuổi nợ phải thu theo khách hàng", summ,
               "Đề xuất khách hàng cần ưu tiên thu, mức trích lập dự phòng nợ khó đòi cần xem xét.", key="ai_ar")
