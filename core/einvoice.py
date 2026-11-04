"""
Đọc file XML hóa đơn điện tử Việt Nam (định dạng theo Thông tư 78/2021/TT-BTC).

Không cần AI: XML là dữ liệu gốc nên đọc trực tiếp sẽ chính xác tuyệt đối.
Cấu trúc thường gặp:
  HDon / DLHDon / TTChung  : KHMSHDon (mẫu số), KHHDon (ký hiệu), SHDon (số), NLap (ngày lập)
  HDon / DLHDon / NDHDon / NBan : Ten, MST, DChi        (người bán)
  HDon / DLHDon / NDHDon / NMua : Ten, MST, DChi        (người mua)
  HDon / DLHDon / NDHDon / DSHHDVu / HHDVu : STT, THHDVu, DVTinh, SLuong, DGia, ThTien, TSuat
  HDon / DLHDon / NDHDon / TToan : TgTCThue, TgTThue, TgTTTBSo
  HDon / MCCQT (mã của cơ quan thuế, có thể không có)

Mỗi nhà cung cấp hóa đơn (VNPT, Viettel, MISA, BKAV...) có thể lồng thêm thẻ,
nên hàm dưới đây tìm thẻ theo TÊN ở bất kỳ cấp nào, không phụ thuộc đường dẫn cứng.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict


def _local(tag: str) -> str:
    """Bỏ namespace: '{ns}SHDon' -> 'SHDon'."""
    return tag.rsplit("}", 1)[-1]


def _find(node, name):
    if node is None:
        return None
    for el in node.iter():
        if _local(el.tag) == name:
            return el
    return None


def _text(node, name, default=""):
    el = _find(node, name)
    return (el.text or "").strip() if el is not None and el.text else default


def _num(value: str) -> float:
    if value in ("", None):
        return 0.0
    try:
        return float(str(value).replace(",", ""))
    except ValueError:
        return 0.0


@dataclass
class InvoiceLine:
    stt: str
    ten_hang: str
    dvt: str
    so_luong: float
    don_gia: float
    thanh_tien: float
    thue_suat: str


@dataclass
class Invoice:
    file: str
    mau_so: str
    ky_hieu: str
    so_hd: str
    ngay_lap: str
    ten_ban: str
    mst_ban: str
    ten_mua: str
    mst_mua: str
    tien_truoc_thue: float
    tien_thue: float
    tong_thanh_toan: float
    ma_cqt: str
    lines: list[InvoiceLine] = field(default_factory=list)
    canh_bao: list[str] = field(default_factory=list)

    def header_dict(self) -> dict:
        d = asdict(self)
        d.pop("lines")
        d["canh_bao"] = "; ".join(self.canh_bao)
        return d


def parse_invoice(xml_bytes: bytes, file_name: str = "") -> Invoice:
    root = ET.fromstring(xml_bytes)
    ttchung = _find(root, "TTChung")
    nban = _find(root, "NBan")
    nmua = _find(root, "NMua")
    ttoan = _find(root, "TToan")

    inv = Invoice(
        file=file_name,
        mau_so=_text(ttchung, "KHMSHDon"),
        ky_hieu=_text(ttchung, "KHHDon"),
        so_hd=_text(ttchung, "SHDon"),
        ngay_lap=_text(ttchung, "NLap"),
        ten_ban=_text(nban, "Ten"),
        mst_ban=_text(nban, "MST"),
        ten_mua=_text(nmua, "Ten"),
        mst_mua=_text(nmua, "MST"),
        tien_truoc_thue=_num(_text(ttoan, "TgTCThue")),
        tien_thue=_num(_text(ttoan, "TgTThue")),
        tong_thanh_toan=_num(_text(ttoan, "TgTTTBSo")),
        ma_cqt=_text(root, "MCCQT"),
    )
    for el in root.iter():
        if _local(el.tag) == "HHDVu":
            inv.lines.append(InvoiceLine(
                stt=_text(el, "STT"),
                ten_hang=_text(el, "THHDVu"),
                dvt=_text(el, "DVTinh"),
                so_luong=_num(_text(el, "SLuong")),
                don_gia=_num(_text(el, "DGia")),
                thanh_tien=_num(_text(el, "ThTien")),
                thue_suat=_text(el, "TSuat"),
            ))
    _validate(inv)
    return inv


def _validate(inv: Invoice, tol: float = 1.0) -> None:
    """Kiểm tra số học – giống kế toán viên rà lại hóa đơn."""
    if not inv.so_hd:
        inv.canh_bao.append("Thiếu số hóa đơn")
    if not inv.mst_ban:
        inv.canh_bao.append("Thiếu MST người bán")
    if not inv.ma_cqt:
        inv.canh_bao.append("Không có mã CQT – kiểm tra loại hóa đơn")
    total_lines = sum(l.thanh_tien for l in inv.lines)
    if inv.lines and abs(total_lines - inv.tien_truoc_thue) > tol:
        inv.canh_bao.append(f"Tổng dòng hàng {total_lines:,.0f} ≠ tiền trước thuế {inv.tien_truoc_thue:,.0f}")
    if abs(inv.tien_truoc_thue + inv.tien_thue - inv.tong_thanh_toan) > tol:
        inv.canh_bao.append("Tiền trước thuế + thuế ≠ tổng thanh toán")
    for l in inv.lines:
        if l.so_luong and l.don_gia and abs(l.so_luong * l.don_gia - l.thanh_tien) > tol:
            inv.canh_bao.append(f"Dòng {l.stt}: SL × đơn giá ≠ thành tiền")


def to_fast_rows(invoices: list[Invoice], columns) -> list[dict]:
    """Trải phẳng hóa đơn thành dòng theo mẫu import FAST (cấu hình trong config.py)."""
    rows = []
    for inv in invoices:
        head = inv.header_dict()
        for l in inv.lines or [None]:
            src = {**head, **(asdict(l) if l else {})}
            rows.append({label: src.get(key, "") for label, key in columns})
    return rows
