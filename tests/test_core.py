"""Kiểm tra nhanh phần lõi: python -m pytest -q  (chạy tao_du_lieu_mau.py trước)"""
from datetime import date
from pathlib import Path

import pandas as pd

from core import config as C
from core.analysis import ar_aging, ar_summary, bank_reconcile, financial_ratios, plan_vs_actual, slow_moving
from core.einvoice import parse_invoice, to_fast_rows

S = Path(__file__).resolve().parent.parent / "du_lieu_mau"


def test_invoice_parse_and_validate():
    invs = [parse_invoice(p.read_bytes(), p.name) for p in sorted((S / "hoa_don_xml").glob("*.xml"))]
    assert len(invs) == 5 and all(i.so_hd and i.mst_ban and i.lines for i in invs)
    assert invs[-1].canh_bao  # hóa đơn mẫu cố ý sai tổng
    assert not invs[0].canh_bao
    rows = to_fast_rows(invs, C.FAST_IMPORT_COLUMNS)
    assert rows and set(rows[0]) == {c for c, _ in C.FAST_IMPORT_COLUMNS}


def test_bank_recon():
    m, ob, os_ = bank_reconcile(pd.read_excel(S / "sao_ke_ngan_hang.xlsx"), pd.read_excel(S / "so_tien_gui_FAST.xlsx"))
    assert len(ob) == 2 and len(os_) == 1 and len(m) == 23


def test_aging_inventory_plan_ratios():
    aged = ar_aging(pd.read_excel(S / "cong_no_phai_thu.xlsx"), date.today())
    assert (aged["con_no"] > 0).all() and len(ar_summary(aged)) > 0
    inv = slow_moving(pd.read_excel(S / "ton_kho.xlsx"))
    assert "Chưa từng xuất" in set(inv["tinh_trang"])
    p = plan_vs_actual(pd.read_excel(S / "ke_hoach_san_pham.xlsx"))
    assert p["ty_le"].notna().all()
    r = financial_ratios(dict(tai_san_ngan_han=120, hang_ton_kho=20, phai_thu=10, tong_tai_san=200, no_ngan_han=100,
                              tong_no=100, von_chu_so_huu=100, doanh_thu=365, gia_von=300, loi_nhuan_sau_thue=10))
    assert abs(r.set_index("Chỉ số").loc["Thanh toán hiện hành", "Giá trị"] - 1.2) < 1e-9
