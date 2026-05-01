"""
Bangkok Transit RAG Engine
ใช้ข้อมูลจาก tourism_metadata.json เป็น Source of Truth
รองรับทั้ง FAISS semantic search และ structured keyword search
"""

import json
import re
import numpy as np
import os  # เพิ่มสำหรับการดึง API Key
from pathlib import Path
from typing import Optional

# ─── paths ────────────────────────────────────────────────
_BASE = Path(__file__).parent.parent / "backend" / "data"
_META_PATH  = _BASE / "tourism_metadata.json"
_INDEX_PATH = _BASE / "tourism_faiss.index"

# ─── load metadata once ────────────────────────────────────
def _load_metadata() -> list[dict]:
    with open(_META_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

_PLACES: list[dict] = _load_metadata()

# ─── precompute lookup sets ────────────────────────────────
ALL_STATIONS: list[str] = sorted(set(p["station"] for p in _PLACES))
ALL_CATEGORIES: list[str] = sorted(set(p["category"] for p in _PLACES))

# Multi-station index: รองรับ "BTS สยาม/จุฬาฯ" → index ทั้ง 'bts สยาม' และ 'จุฬาฯ'
_STATION_INDEX: dict[str, list[dict]] = {}
for _p in _PLACES:
    for _s in re.split(r"[/,]", _p["station"]):
        _key = _s.strip().lower()
        _STATION_INDEX.setdefault(_key, []).append(_p)

# จุดที่ 2 — แก้ไข extract_intent logic (เพิ่ม manual alias ต่อท้าย loop เดิม)[cite: 4]
# Manual alias สำหรับชื่อย่อทั่วไป
_STATION_ALIASES = {
    "ทองหล่อ": "BTS ทองหล่อ",
    "อโศก": "BTS อโศก",
    "สยาม": "BTS สยาม",
    "เอกมัย": "BTS เอกมัย",
    "หมอชิต": "MRT จตุจักร/BTS หมอชิต",
    "จตุจักร": "MRT จตุจักร",
    "เพชรบุรี": "MRT เพชรบุรี",
    "พหลโยธิน": "MRT พหลโยธิน",
    "กำแพงเพชร": "MRT กำแพงเพชร",
}
for _alias, _station_name in _STATION_ALIASES.items():
    if _alias not in _STATION_INDEX:
        # ชี้ไปที่ places ของสถานีจริง
        _real_places = [p for p in _PLACES if _station_name in p["station"]]
        if _real_places:
            _STATION_INDEX[_alias] = _real_places

# ─── optional FAISS semantic search ───────────────────────
try:
    import faiss
    _faiss_index = faiss.read_index(str(_INDEX_PATH))
    _FAISS_AVAILABLE = True
except Exception:
    _faiss_index = None
    _FAISS_AVAILABLE = False

# เพิ่มตรงนี้หลัง _FAISS_AVAILABLE = False โดยห้ามแก้ code ส่วนอื่น
_BGE_MODEL = None

def _get_bge_model():
    global _BGE_MODEL
    if _BGE_MODEL is None:
        from sentence_transformers import SentenceTransformer
        _BGE_MODEL = SentenceTransformer("BAAI/bge-m3")
    return _BGE_MODEL

def _embed_query(query: str) -> Optional[np.ndarray]:
    """สร้าง embedding ด้วย BAAI/bge-m3 (ตรงกับ FAISS index ที่ทีมสร้างไว้)"""
    try:
        model = _get_bge_model()
        vec = model.encode(query, normalize_embeddings=True)
        return np.array(vec, dtype=np.float32).reshape(1, -1)
    except Exception:
        return None


# ─────────────────────────────────────────────────────────
# Tool Functions (เรียกใช้ใน Agent Loop)
# ─────────────────────────────────────────────────────────

def search_by_station(station: str) -> list[dict]:
    """
    ค้นหาสถานที่ตามชื่อสถานีรถไฟฟ้า BTS/MRT
    รองรับ partial match เช่น 'สยาม' เจอ 'BTS สยาม'
    รองรับสถานีคู่ เช่น 'BTS ชิดลม/สยาม'
    """
    station_q = station.strip().lower()
    seen, results = set(), []
    for key, places in _STATION_INDEX.items():
        if station_q in key:
            for p in places:
                if p["name"] not in seen:
                    seen.add(p["name"])
                    results.append(p)
    return results


def search_by_category(category: str) -> list[dict]:
    """
    กรองตามหมวดหมู่ รองรับ partial match
    Categories จริง:
      - สถานที่ทางศาสนา และวัด
      - พิพิธภัณฑ์และศูนย์การเรียนรู้เชิงทัศนศึกษา
      - ศูนย์การค้า ตลาด และห้างสรรพสินค้า
      - คาเฟ่
      - พื้นที่สีเขียว และจุดชมวิวเมือง
    """
    cat_q = category.strip().lower()
    return [p for p in _PLACES if cat_q in p["category"].lower()]


def search_by_station_and_category(station: str, category: str) -> list[dict]:
    """ค้นหาแบบผสม: สถานี + หมวดหมู่"""
    by_station = {p["name"]: p for p in search_by_station(station)}
    cat_q = category.strip().lower()
    return [p for p in by_station.values() if cat_q in p["category"].lower()]


def semantic_search(query: str, top_k: int = 5) -> list[dict]:
    """
    Semantic search ผ่าน FAISS index ที่ทีมสร้างไว้
    Fallback เป็น full_text_search ถ้า FAISS/embedding ไม่พร้อม
    """
    if _FAISS_AVAILABLE and _faiss_index is not None:
        vec = _embed_query(query)
        if vec is not None:
            distances, indices = _faiss_index.search(vec, top_k)
            results = []
            for idx in indices[0]:
                if 0 <= idx < len(_PLACES):
                    results.append(_PLACES[idx])
            return results
    return full_text_search(query)


def full_text_search(query: str) -> list[dict]:
    """Keyword search ใน name, details, full_text — ใช้เป็น fallback"""
    q = query.strip().lower()
    return [
        p for p in _PLACES
        if q in p.get("name", "").lower()
        or q in p.get("details", "").lower()
        or q in p.get("full_text", "").lower()
    ]


def get_all_stations() -> list[str]:
    """รายชื่อสถานีทั้งหมดที่มีข้อมูล"""
    return ALL_STATIONS


def get_all_categories() -> list[str]:
    """หมวดหมู่ทั้งหมด"""
    return ALL_CATEGORIES


# ─────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────

_CATEGORY_ALIASES: dict[str, str] = {
    # วัด / ศาสนา
    "วัด": "สถานที่ทางศาสนา", "ไหว้พระ": "สถานที่ทางศาสนา",
    "ศาสนา": "สถานที่ทางศาสนา", "ศาล": "สถานที่ทางศาสนา",
    "พระ": "สถานที่ทางศาสนา",
    # พิพิธภัณฑ์
    "พิพิธภัณฑ์": "พิพิธภัณฑ์", "museum": "พิพิธภัณฑ์",
    "เรียนรู้": "พิพิธภัณฑ์", "ท้องฟ้าจำลอง": "พิพิธภัณฑ์",
    # คาเฟ่
    "คาเฟ่": "คาเฟ่", "กาแฟ": "คาเฟ่", "ชา": "คาเฟ่",
    "นั่งเล่น": "คาเฟ่", "cafe": "คาเฟ่", "ร้านกาแฟ": "คาเฟ่",
    # ช้อปปิ้ง / ตลาด
    "ห้าง": "ศูนย์การค้า", "ช้อป": "ศูนย์การค้า",
    "ตลาด": "ศูนย์การค้า", "mall": "ศูนย์การค้า",
    "ซื้อของ": "ศูนย์การค้า",
    # สวน / ชมวิว
    "สวน": "พื้นที่สีเขียว", "ชมวิว": "พื้นที่สีเขียว",
    "ธรรมชาติ": "พื้นที่สีเขียว", "วิว": "พื้นที่สีเขียว",
    "สีเขียว": "พื้นที่สีเขียว",
}


def format_place_card(place: dict) -> str:
    """แปลง place dict → text สำหรับส่งให้ Gemini"""
    return (
        f"สถานที่: {place['name']}\n"
        f"หมวดหมู่: {place['category']}\n"
        f"สถานี: {place['station']}\n"
        f"รายละเอียด: {place['details']}"
    )


def extract_intent(query: str) -> dict:
    """วิเคราะห์ query เบื้องต้นสำหรับ Step 1 ของ Agent Loop"""
    q = query.lower()

    # หาสถานีที่ match ยาวที่สุด (greedy)
    found_station = None
    best_len = 0
    for key, places in _STATION_INDEX.items():
        if key in q and len(key) > best_len:
            found_station = places[0]["station"]
            best_len = len(key)

    # หา category จาก alias
    found_category = None
    for alias, cat in _CATEGORY_ALIASES.items():
        if alias in q:
            found_category = cat
            break

    return {"station": found_station, "category": found_category, "raw_query": query}