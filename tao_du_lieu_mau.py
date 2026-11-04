"""Tạo dữ liệu mẫu để chạy thử app: python tao_du_lieu_mau.py"""
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

random.seed(7)
OUT = Path(__file__).parent / "du_lieu_mau"
OUT.mkdir(exist_ok=True)
(OUT / "hoa_don_xml").mkdir(exist_ok=True)
TODAY = date.today()

NCC = [("Công ty TNHH Canon Marketing Việt Nam", "0301234567"),
       ("Công ty CP Phân phối Ricoh Việt Nam", "0109876543"),
       ("Công ty TNHH Fujifilm Business Innovation VN", "0312223334")]
HANG = [("Mực Canon NPG-59", "Hộp", 450_000), ("Drum Ricoh MP 2014", "Cái", 1_250_000),
        ("Máy photocopy Ricoh IM 2702", "Chiếc", 38_500_000), ("Cụm sấy Fuji Apeos C3060", "Bộ", 4_800_000),
        ("Giấy A4 Double A 70gsm", "Ram", 72_000)]


def xml_invoice(i, ncc, lines, broken=False):
    rows, total = [], 0
    for n, (ten, dvt, gia, sl) in enumerate(lines, 1):
        tt = gia * sl
        total += tt
        rows.append(f"<HHDVu><TChat>1</TChat><STT>{n}</STT><THHDVu>{ten}</THHDVu><DVTinh>{dvt}</DVTinh>"
                    f"<SLuong>{sl}</SLuong><DGia>{gia}</DGia><ThTien>{tt}</ThTien><TSuat>10%</TSuat></HHDVu>")
    vat = round(total * 0.1)
    pay = total + vat + (50_000 if broken else 0)
    d = (TODAY - timedelta(days=random.randint(1, 25))).isoformat()
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<HDon><DLHDon Id="data"><TTChung><PBan>2.0.1</PBan><THDon>Hóa đơn giá trị gia tăng</THDon>
<KHMSHDon>1</KHMSHDon><KHHDon>C26TAA</KHHDon><SHDon>{1000 + i}</SHDon><NLap>{d}</NLap><DVTTe>VND</DVTTe></TTChung>
<NDHDon><NBan><Ten>{ncc[0]}</Ten><MST>{ncc[1]}</MST><DChi>Hà Nội</DChi></NBan>
<NMua><Ten>Công ty CP Tập đoàn Đầu tư Tân Hồng Hà</Ten><MST>0100000001</MST><DChi>Hà Nội</DChi></NMua>
<DSHHDVu>{''.join(rows)}</DSHHDVu>
<TToan><TgTCThue>{total}</TgTCThue><TgTThue>{vat}</TgTThue><TgTTTBSo>{pay}</TgTTTBSo></TToan></NDHDon></DLHDon>
<MCCQT>00A1B2C3D4E5F6{i:04d}</MCCQT></HDon>"""


for i in range(5):
    lines = [(*random.choice(HANG), random.randint(1, 10)) for _ in range(random.randint(1, 3))]
    (OUT / "hoa_don_xml" / f"HD_{1000 + i}.xml").write_text(xml_invoice(i, random.choice(NCC), lines, broken=(i == 4)), encoding="utf-8")

# Sao kê ngân hàng + sổ tiền gửi FAST
bank, book = [], []
for i in range(25):
    d = TODAY - timedelta(days=random.randint(1, 30))
    amt = random.choice([1, -1]) * random.randint(5, 300) * 100_000
    so_ct = f"{'BC' if amt > 0 else 'UNC'}{i:04d}"
    bank.append({"Ngày giao dịch": d.strftime("%d/%m/%Y"), "Số tiền": amt,
                 "Nội dung": f"{'KH thanh toan' if amt > 0 else 'Thanh toan NCC'} {so_ct}" if i % 3 else "Chuyen tien",
                 "Số tham chiếu": f"FT{random.randint(10**8, 10**9)}"})
    if i not in (3, 11):  # 2 giao dịch chưa hạch toán
        dd = d + timedelta(days=random.choice([0, 0, 1, 2]))
        book.append({"Ngày CT": dd.strftime("%d/%m/%Y"), "Số CT": so_ct, "PS Nợ": max(amt, 0), "PS Có": max(-amt, 0),
                     "Diễn giải": "Thu tiền khách hàng" if amt > 0 else "Chi trả nhà cung cấp"})
book.append({"Ngày CT": TODAY.strftime("%d/%m/%Y"), "Số CT": "BC9999", "PS Nợ": 12_345_000, "PS Có": 0, "Diễn giải": "Ghi sổ nhưng NH chưa báo có"})
pd.DataFrame(bank).to_excel(OUT / "sao_ke_ngan_hang.xlsx", index=False)
pd.DataFrame(book).to_excel(OUT / "so_tien_gui_FAST.xlsx", index=False)

# Công nợ
KH = [("KH001", "Trường THPT Chu Văn An"), ("KH002", "Bệnh viện Đa khoa Đức Giang"), ("KH003", "Công ty CP Xây dựng Hà Đô"),
      ("KH004", "UBND Quận Cầu Giấy"), ("KH005", "Ngân hàng TMCP Á Châu – CN Hà Nội"), ("KH006", "Công ty TNHH Logistics Bắc Việt")]
ar = []
for i in range(40):
    kh = random.choice(KH)
    d = TODAY - timedelta(days=random.randint(5, 200))
    pt = random.randint(5, 150) * 1_000_000
    ar.append({"Mã KH": kh[0], "Tên khách hàng": kh[1], "Số hóa đơn": f"{2000 + i}", "Ngày hóa đơn": d.strftime("%d/%m/%Y"),
               "Hạn thanh toán": (d + timedelta(days=30)).strftime("%d/%m/%Y"), "Phải thu": pt,
               "Đã thu": random.choice([0, 0, pt, pt // 2]), "NV kinh doanh": random.choice(["Hương", "Tuấn", "Minh"])})
pd.DataFrame(ar).to_excel(OUT / "cong_no_phai_thu.xlsx", index=False)

# Tồn kho
inv = []
for i, (ten, dvt, gia) in enumerate(HANG * 3):
    sl = random.randint(0, 60)
    last = TODAY - timedelta(days=random.choice([5, 20, 45, 100, 150, 220, 400]))
    inv.append({"Mã vật tư": f"VT{i:03d}", "Tên vật tư": ten, "Kho": random.choice(["Kho HN", "Kho HCM"]), "SL tồn": sl,
                "Giá trị tồn": sl * gia, "Ngày xuất cuối": "" if i == 7 else last.strftime("%d/%m/%Y")})
pd.DataFrame(inv).to_excel(OUT / "ton_kho.xlsx", index=False)

# Kế hoạch sản phẩm
plan = [("Máy photocopy", 12_000, 10_150), ("Máy in", 4_500, 4_820), ("Vật tư – mực, drum", 6_000, 4_300),
        ("Dịch vụ cho thuê máy", 3_200, 3_050), ("Dịch vụ bảo trì", 1_800, 1_950), ("Máy chiếu – thiết bị khác", 2_500, 1_600)]
pd.DataFrame(plan, columns=["Nhóm sản phẩm", "Kế hoạch doanh thu", "Thực hiện"]).to_excel(OUT / "ke_hoach_san_pham.xlsx", index=False)
print("Đã tạo dữ liệu mẫu trong", OUT)
