import pandas as pd
import streamlit as st

from core import ai
from core.ui import download_excel

st.title("2. Đọc chứng từ ảnh / scan / PDF bằng AI")
st.caption("Dùng cho chứng từ KHÔNG có XML: hóa đơn giấy, phiếu thu chi, biên bản, ảnh chụp. "
           "Có XML thì dùng trang 1 – chính xác hơn.")

if ai.provider() is None:
    st.warning("Cần khóa AI: tạo file .env với GEMINI_API_KEY=... (khuyên dùng Gemini vì đọc PDF trực tiếp).")

files = st.file_uploader("Chọn ảnh hoặc PDF", type=["png", "jpg", "jpeg", "pdf"], accept_multiple_files=True)
if files and st.button("Đọc bằng AI", disabled=ai.provider() is None):
    heads, lines = [], []
    bar = st.progress(0.0)
    for n, f in enumerate(files, 1):
        mime = "application/pdf" if f.name.lower().endswith(".pdf") else f"image/{'jpeg' if f.name.lower().endswith(('jpg', 'jpeg')) else 'png'}"
        try:
            d = ai.read_document(f.read(), mime)
        except Exception as e:
            d = {"loi": str(e)}
        rows = d.pop("dong_hang", []) or []
        heads.append({"file": f.name, **d})
        lines += [{"file": f.name, **r} for r in rows]
        bar.progress(n / len(files))
    h, l = pd.DataFrame(heads), pd.DataFrame(lines)
    st.subheader("Thông tin chứng từ")
    st.data_editor(h, hide_index=True, use_container_width=True, key="h")
    st.subheader("Dòng hàng")
    st.data_editor(l, hide_index=True, use_container_width=True, key="l")
    st.info("Kiểm tra cột 'do_tin_cay' và 'ghi_chu'. Chứng từ độ tin cậy thấp phải đối chiếu bản gốc.")
    download_excel({"Chung tu": h, "Dong hang": l}, "chung_tu_AI.xlsx")
