"""Thành phần giao diện dùng chung cho các trang."""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import streamlit as st

from . import ai

SAMPLE = Path(__file__).resolve().parent.parent / "du_lieu_mau"


def money(x):
    try:
        return f"{x:,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return x


def short(x):
    """Số tiền gọn cho ô chỉ số: 2.056,5 tr / 1,2 tỷ."""
    try:
        x = float(x)
    except (TypeError, ValueError):
        return x
    if abs(x) >= 1e9:
        return f"{x / 1e9:,.2f} tỷ".replace(",", "#").replace(".", ",").replace("#", ".")
    return f"{x / 1e6:,.1f} tr".replace(",", "#").replace(".", ",").replace("#", ".")


def load_excel(label: str, sample_name: str, key: str) -> pd.DataFrame | None:
    """Ô tải file Excel; nếu chưa tải, cho phép dùng dữ liệu mẫu."""
    c1, c2 = st.columns([3, 1])
    up = c1.file_uploader(label, type=["xlsx", "xls", "csv"], key=key)
    use_sample = c2.checkbox("Dùng dữ liệu mẫu", value=up is None, key=key + "_sample")
    if up is not None:
        return pd.read_csv(up) if up.name.endswith(".csv") else pd.read_excel(up)
    if use_sample and (SAMPLE / sample_name).exists():
        return pd.read_excel(SAMPLE / sample_name)
    return None


def check_columns(df: pd.DataFrame, mapping: dict, label: str) -> bool:
    missing = [v for v in mapping.values() if v not in df.columns]
    if missing:
        st.error(f"File {label} thiếu cột: {', '.join(missing)}. Sửa tên cột trong core/config.py cho khớp file FAST.")
        st.caption("Các cột đang có: " + ", ".join(map(str, df.columns)))
        return False
    return True


def download_excel(sheets: dict[str, pd.DataFrame], file_name: str, label: str = "Tải file Excel"):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        for name, df in sheets.items():
            df.to_excel(w, sheet_name=name[:31], index=False)
    st.download_button(label, buf.getvalue(), file_name=file_name,
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


def ai_comment(title: str, df: pd.DataFrame, focus: str = "", key: str = "ai"):
    st.subheader("Nhận xét của AI")
    if ai.provider() is None:
        st.info("Chưa bật AI. Thêm GEMINI_API_KEY hoặc OPENAI_API_KEY vào file .env để AI tự viết nhận xét, cảnh báo.")
        return
    if st.button("AI phân tích & cảnh báo", key=key):
        with st.spinner("AI đang đọc số liệu..."):
            try:
                st.markdown(ai.comment(title, df.head(60).to_string(index=False), focus))
            except Exception as e:  # hiển thị lỗi thân thiện
                st.error(f"Lỗi gọi AI: {e}")
