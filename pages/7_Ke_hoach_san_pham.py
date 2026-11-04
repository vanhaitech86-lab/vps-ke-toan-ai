import streamlit as st

from core import config as C
from core.analysis import plan_vs_actual
from core.ui import ai_comment, check_columns, download_excel, load_excel

st.title("7. Phân tích thực hiện kế hoạch sản phẩm")
df = load_excel("Kế hoạch & thực hiện theo nhóm sản phẩm", "ke_hoach_san_pham.xlsx", "plan")

if df is not None and check_columns(df, C.PLAN_COLUMNS, "kế hoạch"):
    d = plan_vs_actual(df)
    tot_p, tot_a = d["ke_hoach"].sum(), d["thuc_hien"].sum()
    c1, c2, c3 = st.columns(3)
    c1.metric("Kế hoạch", f"{tot_p:,.0f}")
    c2.metric("Thực hiện", f"{tot_a:,.0f}", f"{tot_a - tot_p:,.0f}")
    c3.metric("Tỷ lệ hoàn thành", f"{tot_a / tot_p:.0%}" if tot_p else "–")
    st.bar_chart(d.set_index("nhom")[["ke_hoach", "thuc_hien"]], stack=False)
    show = d.assign(ty_le=d["ty_le"].map(lambda x: f"{x:.0%}" if x is not None else "–"))
    st.dataframe(show, hide_index=True, use_container_width=True)
    download_excel({"Thuc hien KH": show}, "thuc_hien_ke_hoach.xlsx")
    ai_comment("Thực hiện kế hoạch doanh thu theo nhóm sản phẩm", show,
               "Chỉ ra nhóm chậm, nguyên nhân có thể và giải pháp cho Kinh doanh.", key="ai_plan")
