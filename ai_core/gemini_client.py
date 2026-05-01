"""
Gemini Client + Agent Loop สำหรับ Bangkok Transit RAG
เวอร์ชันเสถียร: รองรับ Greeting Tool, Retry Logic และดักจับ Empty Content
"""

import os
import json
import time  # สำหรับระบบ Retry
from typing import Optional
from google import genai
from google.genai import types

from .rag_engine import (
    search_by_station,
    search_by_category,
    search_by_station_and_category,
    semantic_search,
    full_text_search,
    get_all_stations,
    get_all_categories,
    format_place_card,
)

# ─────────────────────────────────────────────
# Tool Functions
# ─────────────────────────────────────────────

def _get_muek_jung_info() -> str:
    """ใช้เมื่อผู้ใช้ทักทาย (สวัสดี) หรือสอบถามว่ามัคจังทำอะไรได้บ้าง / แนะนำตัว"""
    info = {
        "name": "มัคจัง (Muek-Jung)",
        "role": "ผู้ช่วย AI ผู้เชี่ยวชาญการท่องเที่ยวตามแนวรถไฟฟ้าในกรุงเทพฯ",
        "capabilities": [
            "แนะนำที่เที่ยว คาเฟ่ ร้านอาหาร วัด และสวนสาธารณะตามแนวรถไฟฟ้า",
            "ค้นหาตามชื่อสถานี (BTS/MRT) หรือค้นหาตามหมวดหมู่ที่สนใจ",
            "ค้นหาด้วยบรรยากาศ (Semantic Search) เช่น 'ที่นั่งทำงานเงียบๆ' หรือ 'ที่ถ่ายรูปสวย'",
            "บอกรายละเอียดการเดินทาง ทางออกสถานี และเวลาเปิด-ปิด"
        ],
        "greeting": "สวัสดีค่ะ! มัคจังพร้อมดูแลแล้วค่ะ อยากให้มัคจังช่วยหาที่เที่ยวแถวไหน หรืออยากไปทำอะไร ถามมาได้เลยนะคะ!"
    }
    return json.dumps(info, ensure_ascii=False)

def _search_by_station(station: str) -> str:
    results = search_by_station(station)
    if not results:
        return json.dumps({"message": "ไม่พบสถานที่ที่ตรงกัน"}, ensure_ascii=False)
    return "\n\n---\n\n".join(format_place_card(p) for p in results)

def _search_by_category(category: str) -> str:
    results = search_by_category(category)
    if not results:
        return json.dumps({"message": "ไม่พบสถานที่ที่ตรงกัน"}, ensure_ascii=False)
    return "\n\n---\n\n".join(format_place_card(p) for p in results)

def _search_by_station_and_category(station: str, category: str) -> str:
    results = search_by_station_and_category(station, category)
    if not results:
        return json.dumps({"message": "ไม่พบสถานที่ที่ตรงกัน"}, ensure_ascii=False)
    return "\n\n---\n\n".join(format_place_card(p) for p in results)

def _semantic_search(query: str) -> str:
    results = semantic_search(query)
    if not results:
        return json.dumps({"message": "ไม่พบสถานที่ที่ตรงกัน"}, ensure_ascii=False)
    return "\n\n---\n\n".join(format_place_card(p) for p in results)

def _get_all_stations() -> str:
    return json.dumps(get_all_stations(), ensure_ascii=False)

def _get_all_categories() -> str:
    return json.dumps(get_all_categories(), ensure_ascii=False)

_TOOL_MAP = {
    "_get_muek_jung_info": (_get_muek_jung_info, None), # ✅ เพิ่ม Tool แนะนำตัว
    "_search_by_station": (_search_by_station, search_by_station),
    "_search_by_category": (_search_by_category, search_by_category),
    "_search_by_station_and_category": (_search_by_station_and_category, search_by_station_and_category),
    "_semantic_search": (_semantic_search, semantic_search),
    "_get_all_stations": (_get_all_stations, None),
    "_get_all_categories": (_get_all_categories, None),
}

# ─────────────────────────────────────────────
# System Prompt (อัปเดตบทบาทการทักทาย)
# ─────────────────────────────────────────────

SYSTEM_PROMPT = """คุณคือ "มัคจัง" ผู้ช่วย AI ที่เชี่ยวชาญเรื่องการท่องเที่ยวตามแนวรถไฟฟ้าในกรุงเทพมหานคร

บทบาท:
- แนะนำสถานที่ท่องเที่ยว ร้านคาเฟ่ วัด พิพิธภัณฑ์ สวน และห้างสรรพสินค้าตามสถานีรถไฟฟ้า
- ใช้ข้อมูลจาก tools เท่านั้น ห้ามแต่งหรือเพิ่มข้อมูลที่ไม่มีในระบบ
- ตอบกลับโดยใช้ภาษาเดียวกับที่ผู้ใช้ถามมา (เช่น ถามไทยตอบไทย, ถามอังกฤษตอบอังกฤษ)

วิธีเลือก tool:
- เมื่อ User ทักทาย (เช่น สวัสดี, สบายดีไหม) หรือถามว่าคุณทำอะไรได้บ้าง -> ต้องเรียก _get_muek_jung_info
- ถามหา "คาเฟ่" -> เรียก _search_by_category(category="คาเฟ่")
- ถามหา "วัด" -> เรียก _search_by_category(category="สถานที่ทางศาสนา")
- รู้ทั้งสถานีและหมวดหมู่ -> เรียก _search_by_station_and_category
- คำถามซับซ้อน/หาบรรยากาศ -> เรียก _semantic_search

วิธีตอบ (AIDA Framework):
1. Attention — ประโยคเปิดดึงดูด
2. Interest — รายละเอียดสถานที่
3. Desire — ความน่าสนใจ
4. Action — วิธีการเดินทาง

กฎเหล็ก:
- ต้องเรียก tool ก่อนตอบเสมอ ห้ามตอบจากความจำ
- หาก User ทักทาย ให้ใช้ข้อมูลจาก _get_muek_jung_info มาแนะนำตัวและชวนคุยเรื่องเที่ยวต่อทันที"""

# ─────────────────────────────────────────────
# Agent
# ─────────────────────────────────────────────

class BangkokRAGAgent:
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            raise ValueError("ต้องใส่ GEMINI_API_KEY ใน environment variable")

        self.client = genai.Client(api_key=key)
        self.tools = [
            _get_muek_jung_info, # เพิ่ม Tool แนะนำตัวเข้าไปในรายการ
            _search_by_station,
            _search_by_category,
            _search_by_station_and_category,
            _semantic_search,
            _get_all_stations,
            _get_all_categories,
        ]
        
        self.config_any = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=self.tools,
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="ANY")
            ),
        )
        self.config_auto = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=self.tools,
            tool_config=types.ToolConfig(
                function_calling_config=types.FunctionCallingConfig(mode="AUTO")
            ),
        )

    def chat(self, user_message: str, history: list[dict] = None) -> dict:
        """Agent Loop — ป้องกัน 503 และข้อความว่าง"""

        contents = []
        for msg in (history or []):
            txt = msg.get("content", "").strip()
            if not txt: continue
            
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(
                role=role,
                parts=[types.Part(text=txt)]
            ))
            
        contents.append(types.Content(
            role="user",
            parts=[types.Part(text=user_message)]
        ))

        tools_used = []
        places_found = []
        candidate = None

        for i in range(5):
            config = self.config_any if i == 0 else self.config_auto

            max_retries = 3
            response = None
            for retry_count in range(max_retries):
                try:
                    response = self.client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=contents,
                        config=config,
                    )
                    break 
                except Exception as e:
                    if "503" in str(e) and retry_count < max_retries - 1:
                        time.sleep(1.5)
                        continue
                    raise e

            if not response or not response.candidates:
                break

            candidate = response.candidates[0]
            contents.append(candidate.content)

            tool_response_parts = []
            has_tool_call = False

            if candidate.content.parts:
                for part in candidate.content.parts:
                    if part.function_call:
                        has_tool_call = True
                        fn_name = part.function_call.name
                        fn_args = dict(part.function_call.args)
                        tools_used.append({"tool": fn_name, "args": fn_args})

                        wrapper_fn, raw_fn = _TOOL_MAP.get(fn_name, (None, None))
                        if wrapper_fn:
                            result_str = wrapper_fn(**fn_args)
                        else:
                            result_str = json.dumps({"error": f"ไม่พบ tool: {fn_name}"}, ensure_ascii=False)

                        if raw_fn:
                            try:
                                raw = raw_fn(**fn_args)
                                if isinstance(raw, list):
                                    places_found.extend(raw)
                            except Exception: pass

                        tool_response_parts.append(
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=fn_name,
                                    response={"result": result_str},
                                )
                            )
                        )

            if not has_tool_call:
                break

            contents.append(types.Content(role="user", parts=tool_response_parts))

        final_text = ""
        if candidate and candidate.content.parts:
            for part in candidate.content.parts:
                if hasattr(part, "text") and part.text:
                    final_text += part.text

        if not final_text.strip():
            final_text = "มัคจังพยายามหาข้อมูลให้แล้ว แต่ยังไม่พบข้อมูลที่ตรงกันเลยค่ะ ลองระบุชื่อสถานีหรือหมวดหมู่ที่เที่ยวดูไหมคะ? 🚇"

        seen, unique = set(), []
        for p in places_found:
            key = p.get("name", "")
            if key not in seen:
                seen.add(key)
                unique.append(p)

        return {
            "response": final_text,
            "places_found": unique,
            "tools_used": tools_used,
        }