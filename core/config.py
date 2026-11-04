"""
CẤU HÌNH CHUNG – sửa file này để khớp với file Excel xuất từ phần mềm FAST của công ty.

Mỗi chức năng đọc file Excel theo TÊN CỘT. Nếu file FAST xuất ra có tên cột khác
(ví dụ "Ngày CT" thay vì "ngay"), chỉ cần sửa phần bên phải dấu ":" ở đây,
không phải sửa code của từng trang.
"""

# ---------- 1. Đối chiếu ngân hàng ----------
# Sao kê ngân hàng (file Excel tải từ internet banking)
BANK_COLUMNS = {
    "ngay": "Ngày giao dịch",
    "so_tien": "Số tiền",          # thu dương, chi âm  (hoặc dùng 2 cột Nợ/Có bên dưới)
    "noi_dung": "Nội dung",
    "so_ct": "Số tham chiếu",
}
# Sổ tiền gửi ngân hàng xuất từ FAST (TK 112)
FAST_BANK_COLUMNS = {
    "ngay": "Ngày CT",
    "so_ct": "Số CT",
    "thu": "PS Nợ",                # tiền vào
    "chi": "PS Có",                # tiền ra
    "dien_giai": "Diễn giải",
}
RECON_DAY_TOLERANCE = 3            # chênh lệch ngày tối đa khi ghép giao dịch

# ---------- 2. Công nợ phải thu ----------
AR_COLUMNS = {
    "ma_kh": "Mã KH",
    "ten_kh": "Tên khách hàng",
    "so_hd": "Số hóa đơn",
    "ngay_hd": "Ngày hóa đơn",
    "han_tt": "Hạn thanh toán",
    "phai_thu": "Phải thu",
    "da_thu": "Đã thu",
    "nv_kd": "NV kinh doanh",
}
AR_DEFAULT_TERM_DAYS = 30          # dùng khi file không có cột hạn thanh toán
AR_BUCKETS = [(0, "Trong hạn"), (1, "1–30 ngày"), (31, "31–60 ngày"), (61, "61–90 ngày"), (91, "> 90 ngày (khó đòi)")]

# ---------- 3. Tồn kho ----------
INV_COLUMNS = {
    "ma_vt": "Mã vật tư",
    "ten_vt": "Tên vật tư",
    "kho": "Kho",
    "sl_ton": "SL tồn",
    "gt_ton": "Giá trị tồn",
    "ngay_xuat_cuoi": "Ngày xuất cuối",
}
SLOW_MOVING_DAYS = 90              # không xuất quá số ngày này = chậm luân chuyển
DEAD_STOCK_DAYS = 180              # không xuất quá số ngày này = tồn đọng

# ---------- 4. Kế hoạch sản phẩm ----------
PLAN_COLUMNS = {
    "nhom": "Nhóm sản phẩm",
    "ke_hoach": "Kế hoạch doanh thu",
    "thuc_hien": "Thực hiện",
}

# ---------- 5. Mẫu xuất file nhập liệu FAST từ hóa đơn ----------
# Cột của file Excel import chứng từ mua hàng vào FAST.
# LƯU Ý: mẫu import thật phụ thuộc phiên bản FAST của công ty – đối chiếu với
# mẫu "Import chứng từ" trong FAST và sửa danh sách/thứ tự cột cho khớp.
FAST_IMPORT_COLUMNS = [
    ("Ngày CT", "ngay_lap"),
    ("Số HĐ", "so_hd"),
    ("Ký hiệu HĐ", "ky_hieu"),
    ("Mã số thuế NCC", "mst_ban"),
    ("Tên NCC", "ten_ban"),
    ("Tên hàng", "ten_hang"),
    ("ĐVT", "dvt"),
    ("Số lượng", "so_luong"),
    ("Đơn giá", "don_gia"),
    ("Thành tiền", "thanh_tien"),
    ("Thuế suất", "thue_suat"),
    ("Mã tra cứu CQT", "ma_cqt"),
]

# ---------- 6. AI ----------
# Đặt khóa API trong file .env (không ghi khóa vào code).
# AI_PROVIDER = "gemini" hoặc "openai"
DEFAULT_AI_PROVIDER = "gemini"
GEMINI_MODEL = "gemini-2.5-flash"
OPENAI_MODEL = "gpt-4.1-mini"
