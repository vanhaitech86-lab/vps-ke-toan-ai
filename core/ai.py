"""
Kết nối AI (Gemini hoặc OpenAI) – dùng cho 2 việc:
  1) Đọc chứng từ ảnh/scan/PDF  -> JSON có cấu trúc
  2) Diễn giải kết quả phân tích  -> nhận xét, cảnh báo bằng tiếng Việt

Khóa API đặt trong file .env:  GEMINI_API_KEY=...  hoặc  OPENAI_API_KEY=...
Chỉ dùng tài khoản AI bản doanh nghiệp / API (dữ liệu không dùng để huấn luyện)
cho số liệu nội bộ, đúng Quy chế sử dụng AI của Tập đoàn.
"""
from __future__ import annotations

import base64
import json
import os
import re

from . import config as C

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DOC_PROMPT = """Bạn là kế toán viên Việt Nam. Đọc chứng từ trong ảnh và trả về DUY NHẤT một JSON:
{"loai_chung_tu": "", "so_chung_tu": "", "ky_hieu": "", "ngay": "dd/mm/yyyy",
 "ten_ben_ban": "", "mst_ben_ban": "", "ten_ben_mua": "", "mst_ben_mua": "",
 "dong_hang": [{"ten_hang": "", "dvt": "", "so_luong": 0, "don_gia": 0, "thanh_tien": 0, "thue_suat": ""}],
 "tien_truoc_thue": 0, "tien_thue": 0, "tong_thanh_toan": 0,
 "do_tin_cay": "cao|trung bình|thấp", "ghi_chu": "chỗ nào mờ/không chắc"}
Số tiền là số nguyên, không có dấu chấm/phẩy. Trường không đọc được để rỗng, KHÔNG đoán."""


def provider() -> str | None:
    p = os.getenv("AI_PROVIDER", C.DEFAULT_AI_PROVIDER)
    if p == "gemini" and os.getenv("GEMINI_API_KEY"):
        return "gemini"
    if p == "openai" and os.getenv("OPENAI_API_KEY"):
        return "openai"
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    return None


def _extract_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0)) if m else {"loi": "AI không trả về JSON", "raw": text}


def ask(prompt: str, file_bytes: bytes | None = None, mime: str = "image/png") -> str:
    p = provider()
    if p is None:
        raise RuntimeError("Chưa cấu hình khóa AI. Tạo file .env với GEMINI_API_KEY hoặc OPENAI_API_KEY.")
    if p == "gemini":
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        parts = [prompt]
        if file_bytes:
            parts.insert(0, types.Part.from_bytes(data=file_bytes, mime_type=mime))
        return client.models.generate_content(model=C.GEMINI_MODEL, contents=parts).text
    from openai import OpenAI
    client = OpenAI()
    content = [{"type": "text", "text": prompt}]
    if file_bytes:
        if mime == "application/pdf":
            raise RuntimeError("Với OpenAI, hãy chuyển PDF sang ảnh trước, hoặc dùng Gemini (đọc PDF trực tiếp).")
        b64 = base64.b64encode(file_bytes).decode()
        content.append({"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}})
    r = client.chat.completions.create(model=C.OPENAI_MODEL, messages=[{"role": "user", "content": content}])
    return r.choices[0].message.content


def read_document(file_bytes: bytes, mime: str) -> dict:
    return _extract_json(ask(DOC_PROMPT, file_bytes, mime))


def comment(title: str, table_text: str, focus: str = "") -> str:
    prompt = (f"Bạn là kế toán trưởng công ty thiết bị văn phòng. Dữ liệu '{title}' như sau:\n{table_text}\n\n"
              f"Hãy viết nhận xét ngắn gọn (tối đa 8 gạch đầu dòng) bằng tiếng Việt: điểm đáng chú ý, rủi ro, "
              f"và việc cần làm ngay, có dẫn số liệu cụ thể. {focus} Không bịa số không có trong dữ liệu.")
    return ask(prompt)
