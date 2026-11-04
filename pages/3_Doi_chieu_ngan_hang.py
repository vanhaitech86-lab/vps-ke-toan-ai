import streamlit as st

from core import config as C
from core.analysis import bank_reconcile
from core.ui import ai_comment, check_columns, download_excel, load_excel, short

st.title("3. Đối chiếu ngân hàng")
st.caption(f"Ghép sao kê với sổ tiền gửi FAST theo số tiền và ngày lệch ≤ {C.RECON_DAY_TOLERANCE} ngày; ưu tiên khi nội dung có số CT.")

bank = load_excel("Sao kê ngân hàng (Excel)", "sao_ke_ngan_hang.xlsx", "bank")
book = load_excel("Sổ tiền gửi ngân hàng xuất từ FAST", "so_tien_gui_FAST.xlsx", "book")

if bank is not None and book is not None and check_columns(bank, C.BANK_COLUMNS, "sao kê") \
        and check_columns(book, C.FAST_BANK_COLUMNS, "sổ FAST"):
    m, ob, os_ = bank_reconcile(bank, book)
    c1, c2, c3 = st.columns(3)
    c1.metric("Đã khớp", len(m))
    c2.metric("Có ở NH, chưa ghi sổ", len(ob), short(ob["Số tiền"].sum()), delta_color="off")
    c3.metric("Đã ghi sổ, NH chưa có", len(os_), short(os_["Số tiền"].sum()), delta_color="off")
    t1, t2, t3 = st.tabs(["Chưa ghi sổ FAST", "Sổ có – NH chưa có", "Đã khớp"])
    t1.dataframe(ob, hide_index=True, use_container_width=True)
    t2.dataframe(os_, hide_index=True, use_container_width=True)
    t3.dataframe(m, hide_index=True, use_container_width=True)
    download_excel({"Chua ghi so": ob, "NH chua co": os_, "Da khop": m}, "doi_chieu_ngan_hang.xlsx")
    ai_comment("Các khoản chênh lệch đối chiếu ngân hàng", ob.assign(Loai="Chưa ghi sổ").merge(os_.assign(Loai="NH chưa có"), how="outer"),
               "Gợi ý giao dịch nào có thể là cùng một khoản bị lệch ngày/số tiền.", key="ai_bank")
