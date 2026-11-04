"""
Các phép phân tích nghiệp vụ kế toán: đối chiếu ngân hàng, tuổi nợ, tồn kho chậm
luân chuyển, chỉ số tài chính, thực hiện kế hoạch. Thuần pandas – không cần AI –
để số liệu luôn chính xác; AI chỉ dùng để diễn giải kết quả.
"""
from __future__ import annotations

from datetime import date

import pandas as pd

from . import config as C


def rename(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    """Đổi tên cột theo config; báo rõ cột nào thiếu."""
    inv = {v: k for k, v in mapping.items()}
    missing = [v for v in mapping.values() if v not in df.columns]
    out = df.rename(columns=inv)
    out.attrs["missing"] = missing
    return out


# ---------------- 1. Đối chiếu ngân hàng ----------------
def bank_reconcile(bank: pd.DataFrame, book: pd.DataFrame, tolerance_days: int = C.RECON_DAY_TOLERANCE):
    """
    Ghép từng giao dịch sao kê với sổ tiền gửi FAST theo: cùng số tiền và lệch ngày ≤ tolerance.
    Ưu tiên ghép khi số tham chiếu/số CT xuất hiện trong nội dung.
    Trả về (khớp, chỉ có ở ngân hàng, chỉ có ở sổ sách).
    """
    b = rename(bank, C.BANK_COLUMNS).copy()
    s = rename(book, C.FAST_BANK_COLUMNS).copy()
    b["ngay"] = pd.to_datetime(b["ngay"], dayfirst=True, errors="coerce")
    s["ngay"] = pd.to_datetime(s["ngay"], dayfirst=True, errors="coerce")
    b["so_tien"] = pd.to_numeric(b["so_tien"], errors="coerce").fillna(0)
    s["so_tien"] = pd.to_numeric(s.get("thu", 0), errors="coerce").fillna(0) - pd.to_numeric(s.get("chi", 0), errors="coerce").fillna(0)
    b["_id"], s["_id"] = range(len(b)), range(len(s))

    used, matches = set(), []
    for _, rb in b.iterrows():
        cand = s[(s["so_tien"].round(0) == round(rb["so_tien"])) & (~s["_id"].isin(used))]
        cand = cand[(cand["ngay"] - rb["ngay"]).abs().dt.days <= tolerance_days]
        if cand.empty:
            continue
        noi_dung = str(rb.get("noi_dung", ""))
        by_ref = cand[cand["so_ct"].astype(str).apply(lambda x: bool(x) and x in noi_dung)]
        pick = (by_ref if not by_ref.empty else cand.assign(_d=(cand["ngay"] - rb["ngay"]).abs()).sort_values("_d")).iloc[0]
        used.add(pick["_id"])
        matches.append({
            "Ngày NH": rb["ngay"].date() if pd.notna(rb["ngay"]) else None,
            "Số tiền": rb["so_tien"],
            "Nội dung NH": noi_dung,
            "Ngày sổ": pick["ngay"].date() if pd.notna(pick["ngay"]) else None,
            "Số CT FAST": pick["so_ct"],
            "Diễn giải FAST": pick.get("dien_giai", ""),
            "Cách ghép": "Theo số CT" if not by_ref.empty else "Theo số tiền + ngày",
        })
        b.loc[b["_id"] == rb["_id"], "_matched"] = True

    only_bank = b[b.get("_matched", pd.Series(False, index=b.index)) != True][["ngay", "so_tien", "noi_dung", "so_ct"]]
    only_book = s[~s["_id"].isin(used)][["ngay", "so_ct", "so_tien", "dien_giai"]]
    only_bank = only_bank.assign(ngay=only_bank["ngay"].dt.date)
    only_book = only_book.assign(ngay=only_book["ngay"].dt.date)
    only_bank.columns = ["Ngày", "Số tiền", "Nội dung", "Số tham chiếu"]
    only_book.columns = ["Ngày", "Số CT", "Số tiền", "Diễn giải"]
    return pd.DataFrame(matches), only_bank.reset_index(drop=True), only_book.reset_index(drop=True)


# ---------------- 2. Tuổi nợ phải thu ----------------
def ar_aging(df: pd.DataFrame, as_of: date | None = None) -> pd.DataFrame:
    d = rename(df, C.AR_COLUMNS).copy()
    as_of = pd.Timestamp(as_of or date.today())
    d["ngay_hd"] = pd.to_datetime(d["ngay_hd"], dayfirst=True, errors="coerce")
    if "han_tt" in d:
        d["han_tt"] = pd.to_datetime(d["han_tt"], dayfirst=True, errors="coerce")
    else:
        d["han_tt"] = pd.NaT
    d["han_tt"] = d["han_tt"].fillna(d["ngay_hd"] + pd.Timedelta(days=C.AR_DEFAULT_TERM_DAYS))
    d["da_thu"] = pd.to_numeric(d.get("da_thu", 0), errors="coerce").fillna(0)
    d["con_no"] = pd.to_numeric(d["phai_thu"], errors="coerce").fillna(0) - d["da_thu"]
    d = d[d["con_no"] > 0].copy()
    d["so_ngay_qua_han"] = (as_of - d["han_tt"]).dt.days.clip(lower=0)

    def bucket(n):
        label = C.AR_BUCKETS[0][1]
        for lo, lab in C.AR_BUCKETS:
            if n >= lo:
                label = lab
        return label

    d["nhom_tuoi_no"] = d["so_ngay_qua_han"].apply(bucket)
    d["ngay_hd"], d["han_tt"] = d["ngay_hd"].dt.date, d["han_tt"].dt.date
    return d


def ar_summary(aged: pd.DataFrame) -> pd.DataFrame:
    order = [b[1] for b in C.AR_BUCKETS]
    p = aged.pivot_table(index=["ma_kh", "ten_kh"], columns="nhom_tuoi_no", values="con_no", aggfunc="sum", fill_value=0)
    p = p.reindex(columns=[c for c in order if c in p.columns])
    p["Tổng còn nợ"] = p.sum(axis=1)
    p["Quá hạn"] = p.drop(columns=[c for c in ["Trong hạn", "Tổng còn nợ"] if c in p.columns]).sum(axis=1)
    return p.sort_values("Quá hạn", ascending=False).reset_index()


# ---------------- 3. Tồn kho chậm luân chuyển ----------------
def slow_moving(df: pd.DataFrame, as_of: date | None = None) -> pd.DataFrame:
    d = rename(df, C.INV_COLUMNS).copy()
    as_of = pd.Timestamp(as_of or date.today())
    d["ngay_xuat_cuoi"] = pd.to_datetime(d["ngay_xuat_cuoi"], dayfirst=True, errors="coerce")
    d["so_ngay_khong_xuat"] = (as_of - d["ngay_xuat_cuoi"]).dt.days
    d["gt_ton"] = pd.to_numeric(d["gt_ton"], errors="coerce").fillna(0)

    def status(n):
        if pd.isna(n):
            return "Chưa từng xuất"
        if n > C.DEAD_STOCK_DAYS:
            return f"Tồn đọng (> {C.DEAD_STOCK_DAYS} ngày)"
        if n > C.SLOW_MOVING_DAYS:
            return f"Chậm luân chuyển (> {C.SLOW_MOVING_DAYS} ngày)"
        return "Bình thường"

    d["tinh_trang"] = d["so_ngay_khong_xuat"].apply(status)
    d["ngay_xuat_cuoi"] = d["ngay_xuat_cuoi"].dt.date
    return d.sort_values("so_ngay_khong_xuat", ascending=False, na_position="first")


# ---------------- 4. Chỉ số tài chính ----------------
RATIO_INPUTS = [
    ("tai_san_ngan_han", "Tài sản ngắn hạn"),
    ("hang_ton_kho", "Hàng tồn kho"),
    ("phai_thu", "Phải thu khách hàng"),
    ("tong_tai_san", "Tổng tài sản"),
    ("no_ngan_han", "Nợ ngắn hạn"),
    ("tong_no", "Tổng nợ phải trả"),
    ("von_chu_so_huu", "Vốn chủ sở hữu"),
    ("doanh_thu", "Doanh thu thuần"),
    ("gia_von", "Giá vốn hàng bán"),
    ("loi_nhuan_sau_thue", "Lợi nhuận sau thuế"),
]


def _div(a, b):
    return a / b if b else None


def financial_ratios(v: dict) -> pd.DataFrame:
    """v: số liệu 1 kỳ theo khóa ở RATIO_INPUTS (đơn vị tùy ý, nhất quán)."""
    rows = [
        ("Thanh toán hiện hành", _div(v["tai_san_ngan_han"], v["no_ngan_han"]), "lần", "≥ 1,2", lambda x: x >= 1.2),
        ("Thanh toán nhanh", _div(v["tai_san_ngan_han"] - v["hang_ton_kho"], v["no_ngan_han"]), "lần", "≥ 0,8", lambda x: x >= 0.8),
        ("Nợ / Vốn chủ sở hữu", _div(v["tong_no"], v["von_chu_so_huu"]), "lần", "≤ 2", lambda x: x <= 2),
        ("Biên lợi nhuận gộp", _div(v["doanh_thu"] - v["gia_von"], v["doanh_thu"]), "%", "theo ngành", None),
        ("Biên lợi nhuận ròng (ROS)", _div(v["loi_nhuan_sau_thue"], v["doanh_thu"]), "%", "> 0", lambda x: x > 0),
        ("ROA", _div(v["loi_nhuan_sau_thue"], v["tong_tai_san"]), "%", "> 0", lambda x: x > 0),
        ("ROE", _div(v["loi_nhuan_sau_thue"], v["von_chu_so_huu"]), "%", "> 0", lambda x: x > 0),
        ("Vòng quay hàng tồn kho", _div(v["gia_von"], v["hang_ton_kho"]), "vòng/kỳ", "càng cao càng tốt", None),
        ("Số ngày thu tiền bình quân", _div(v["phai_thu"] * 365, v["doanh_thu"]), "ngày (năm)", "≤ kỳ hạn tín dụng", None),
    ]
    out = []
    for name, val, unit, ref, ok in rows:
        flag = "" if val is None or ok is None else ("Đạt" if ok(val) else "Cảnh báo")
        out.append({"Chỉ số": name, "Giá trị": val, "Đơn vị": unit, "Ngưỡng tham khảo": ref, "Đánh giá": flag})
    return pd.DataFrame(out)


# ---------------- 5. Kế hoạch sản phẩm ----------------
def plan_vs_actual(df: pd.DataFrame) -> pd.DataFrame:
    d = rename(df, C.PLAN_COLUMNS).copy()
    d["ke_hoach"] = pd.to_numeric(d["ke_hoach"], errors="coerce").fillna(0)
    d["thuc_hien"] = pd.to_numeric(d["thuc_hien"], errors="coerce").fillna(0)
    d["ty_le"] = d.apply(lambda r: r["thuc_hien"] / r["ke_hoach"] if r["ke_hoach"] else None, axis=1)
    d["chenh_lech"] = d["thuc_hien"] - d["ke_hoach"]
    d["danh_gia"] = d["ty_le"].apply(lambda x: "" if x is None else ("Vượt kế hoạch" if x >= 1 else ("Cần theo dõi" if x >= 0.8 else "Chậm kế hoạch")))
    return d.sort_values("ty_le")
