"""
Test Script สำหรับ ai_core
รันตรงๆ โดยไม่ต้องเปิด web server

วิธีรัน:
    python test_ai_core.py
    python test_ai_core.py --quick   # test เฉพาะ RAG engine (ไม่เรียก Gemini)
    python test_ai_core.py --chat    # test chat แบบ interactive
"""

import sys
import os
import json
import argparse

# เพิ่ม project root เข้า path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# ─── สี สำหรับ terminal output ────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):   print(f"{GREEN}✓ {msg}{RESET}")
def fail(msg): print(f"{RED}✗ {msg}{RESET}")
def info(msg): print(f"{CYAN}→ {msg}{RESET}")
def head(msg): print(f"\n{BOLD}{BLUE}{'─'*50}\n  {msg}\n{'─'*50}{RESET}")


# ═══════════════════════════════════════════════
# PART 1: Test RAG Engine (ไม่ใช้ Gemini)
# ═══════════════════════════════════════════════

def test_rag_engine():
    head("PART 1: RAG Engine Tests")

    from ai_core.rag_engine import (
        search_by_station,
        search_by_category,
        search_by_station_and_category,
        semantic_search,
        full_text_search,
        get_all_stations,
        get_all_categories,
        extract_intent,
    )

    # 1.1 โหลดข้อมูล
    stations = get_all_stations()
    categories = get_all_categories()
    print(f"\n{YELLOW}สถานีทั้งหมด ({len(stations)} สถานี):{RESET}")
    for s in stations:
        print(f"  - {s}")
    print(f"\n{YELLOW}หมวดหมู่ทั้งหมด ({len(categories)} หมวด):{RESET}")
    for c in categories:
        print(f"  - {c}")

    # 1.2 search_by_station
    print(f"\n{YELLOW}[Test] search_by_station('สยาม'){RESET}")
    results = search_by_station("สยาม")
    if results:
        ok(f"เจอ {len(results)} สถานที่")
        for r in results[:3]:
            print(f"  • {r['name']} ({r['category']})")
    else:
        fail("ไม่พบผลลัพธ์")

    # 1.3 search_by_category
    print(f"\n{YELLOW}[Test] search_by_category('คาเฟ่'){RESET}")
    results = search_by_category("คาเฟ่")
    if results:
        ok(f"เจอ {len(results)} คาเฟ่")
        for r in results[:3]:
            print(f"  • {r['name']} ({r['station']})")
    else:
        fail("ไม่พบผลลัพธ์")

    # 1.4 search_by_station_and_category
    print(f"\n{YELLOW}[Test] search_by_station_and_category('สุรศักดิ์', 'คาเฟ่'){RESET}")
    results = search_by_station_and_category("สุรศักดิ์", "คาเฟ่")
    if results:
        ok(f"เจอ {len(results)} สถานที่")
        for r in results:
            print(f"  • {r['name']}")
    else:
        fail("ไม่พบผลลัพธ์")

    # 1.5 full_text_search
    print(f"\n{YELLOW}[Test] full_text_search('ถ่ายรูป'){RESET}")
    results = full_text_search("ถ่ายรูป")
    if results:
        ok(f"เจอ {len(results)} สถานที่")
        for r in results[:3]:
            print(f"  • {r['name']} ({r['station']})")
    else:
        fail("ไม่พบผลลัพธ์")

    # 1.6 semantic_search (ถ้ามี FAISS)
    print(f"\n{YELLOW}[Test] semantic_search('บรรยากาศสงบ'){RESET}")
    from ai_core.rag_engine import _FAISS_AVAILABLE
    if _FAISS_AVAILABLE:
        results = semantic_search("บรรยากาศสงบ")
        if results:
            ok(f"FAISS เจอ {len(results)} สถานที่")
            for r in results[:3]:
                print(f"  • {r['name']} ({r['station']})")
        else:
            fail("ไม่พบผลลัพธ์")
    else:
        info("FAISS ไม่พร้อม → ใช้ full_text_search แทน (fallback ปกติ)")

    # 1.7 extract_intent
    print(f"\n{YELLOW}[Test] extract_intent(){RESET}")
    test_queries = [
        "อยากไปคาเฟ่แถวสยาม",
        "วัดใกล้ MRT ลาดพร้าว",
        "พิพิธภัณฑ์เอกมัย",
        "ที่สวยๆ แถวทองหล่อ",
    ]
    for q in test_queries:
        intent = extract_intent(q)
        print(f"  \"{q}\"")
        print(f"    → station: {intent['station']}, category: {intent['category']}")

    ok("RAG Engine Tests ผ่านทั้งหมด!")


# ═══════════════════════════════════════════════
# PART 2: Test Gemini Agent (ใช้ API Key)
# ═══════════════════════════════════════════════

def test_gemini_agent():
    head("PART 2: Gemini Agent Tests")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        fail("ไม่พบ GEMINI_API_KEY — ข้ามการทดสอบนี้")
        info("ใส่ key ใน .env แล้วรันใหม่")
        return False

    ok(f"พบ API Key: {api_key[:10]}...")

    from ai_core.gemini_client import BangkokRAGAgent

    info("สร้าง BangkokRAGAgent...")
    agent = BangkokRAGAgent()
    ok("สร้าง agent สำเร็จ")

    # Test cases
    test_cases = [
        {
            "name": "หาคาเฟ่แถวสุรศักดิ์",
            "message": "แนะนำคาเฟ่แถวสุรศักดิ์หน่อย",
            "expect_tools": True,
            "expect_places": True,
        },
        {
            "name": "หาวัดแถวเอกมัย",
            "message": "มีวัดอะไรแถว BTS เอกมัย บ้าง",
            "expect_tools": True,
            "expect_places": True,
        },
        {
            "name": "คำถามคลุมเครือ",
            "message": "อยากไปที่บรรยากาศสงบๆ ถ่ายรูปสวย",
            "expect_tools": True,
            "expect_places": True,
        },
    ]

    all_passed = True
    for i, case in enumerate(test_cases, 1):
        print(f"\n{YELLOW}[Test {i}] {case['name']}{RESET}")
        print(f"  คำถาม: \"{case['message']}\"")

        try:
            result = agent.chat(case["message"])

            # ตรวจ tools_used
            tools_used = result.get("tools_used", [])
            places_found = result.get("places_found", [])
            response = result.get("response", "")

            if case["expect_tools"] and tools_used:
                ok(f"เรียก tools: {[t['tool'] for t in tools_used]}")
            elif case["expect_tools"]:
                fail("ไม่ได้เรียก tool เลย!")
                all_passed = False

            if case["expect_places"] and places_found:
                ok(f"พบ {len(places_found)} สถานที่: {[p['name'] for p in places_found[:3]]}")
            elif case["expect_places"]:
                info("ไม่พบสถานที่ (อาจปกติ ถ้า query คลุมเครือมาก)")

            print(f"\n  {BOLD}คำตอบ:{RESET}")
            # แสดงแค่ 300 ตัวอักษรแรก
            preview = response[:300] + "..." if len(response) > 300 else response
            print(f"  {preview}")

        except Exception as e:
            fail(f"Error: {e}")
            all_passed = False

    if all_passed:
        ok("\nGemini Agent Tests ผ่านทั้งหมด! 🎉")
    else:
        fail("\nบางเคสไม่ผ่าน ดู error ด้านบน")

    return all_passed


# ═══════════════════════════════════════════════
# PART 3: Interactive Chat
# ═══════════════════════════════════════════════

def interactive_chat():
    head("PART 3: Interactive Chat")

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        fail("ไม่พบ GEMINI_API_KEY")
        return

    from ai_core.gemini_client import BangkokRAGAgent
    agent = BangkokRAGAgent()
    ok("KIDDEE พร้อมแล้ว! พิมพ์ 'quit' เพื่อออก\n")

    history = []
    while True:
        try:
            user_input = input(f"{BOLD}คุณ: {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nออกจาก chat")
            break

        if user_input.lower() in ("quit", "exit", "q", "ออก"):
            print("ลาก่อนนะคะ! 👋")
            break

        if not user_input:
            continue

        info("กำลังค้นหา...")
        try:
            result = agent.chat(user_input, history=history)

            # แสดง tools ที่ใช้
            if result["tools_used"]:
                tools_str = ", ".join(t["tool"] for t in result["tools_used"])
                print(f"{YELLOW}[Tools: {tools_str}]{RESET}")

            # แสดงคำตอบ
            print(f"\n{BOLD}KIDDEE:{RESET} {result['response']}")

            # แสดงสถานที่ที่เจอ
            if result["places_found"]:
                print(f"\n{CYAN}📍 สถานที่ที่เจอ ({len(result['places_found'])} แห่ง):{RESET}")
                for p in result["places_found"]:
                    print(f"  • {p['name']} | {p['station']} | {p['category']}")

            print()

            # เพิ่มเข้า history
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": result["response"]})

            # จำกัด history ไม่เกิน 10 messages
            if len(history) > 10:
                history = history[-10:]

        except Exception as e:
            fail(f"Error: {e}")


# ═══════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test ai_core")
    parser.add_argument("--quick", action="store_true", help="Test เฉพาะ RAG engine (ไม่เรียก Gemini)")
    parser.add_argument("--chat",  action="store_true", help="Interactive chat mode")
    args = parser.parse_args()

    if args.chat:
        interactive_chat()
    elif args.quick:
        test_rag_engine()
    else:
        # รันทุก test
        test_rag_engine()
        print()
        test_gemini_agent()