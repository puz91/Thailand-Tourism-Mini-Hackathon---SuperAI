

# 🚇 Bangkok Transit RAG: "มัคจัง" AI Travel Assistant 🤖

**Bangkok Transit RAG** (หรือน้อง **"มัคจัง"**) คือระบบผู้ช่วยอัจฉริยะที่ออกแบบมาเพื่อยกระดับประสบการณ์การท่องเที่ยวในกรุงเทพมหานครตามแนวรถไฟฟ้า (BTS/MRT) โดยใช้เทคนิค **Retrieval-Augmented Generation (RAG)** ผสมผสานกับ **Agentic Function Calling** เพื่อให้ข้อมูลที่แม่นยำ จริงใจ และเข้าถึงง่าย

---

## 🌟 Key Features (Pro Spec)

*   **Hybrid Search Engine**: ผสมผสานการค้นหาแบบ Metadata Filtering (Station/Category) และ Semantic Search (Vector Embedding) เพื่อความแม่นยำสูงสุด
*   **Agentic Orchestration**: ใช้ Gemini 2.5-flash ในการตัดสินใจเลือกใช้ Tools (Function Calling) ตาม Intent ของผู้ใช้
*   **AIDA Framework Responses**: ปรับแต่งการตอบกลับให้ดึงดูดใจผู้ใช้ (Attention, Interest, Desire, Action) เพื่อกระตุ้นการท่องเที่ยว
*   **Robust Connection**: ระบบ Retry Logic อัตโนมัติเมื่อเกิด Error 503 และระบบ Filtering ป้องกัน Empty History
*   **Modern Tech Stack**: สถาปัตยกรรม Next.js 16 (App Router) เชื่อมต่อกับ FastAPI Backend

---

## 🛠 Tech Architecture

### Frontend
*   **Framework**: Next.js 16 (Turbopack)
*   **UI Components**: Tailwind CSS, Shadcn/UI, Lucide React
*   **State Management**: React Hooks (useRAGChat Custom Hook)

### Backend (AI Core)
*   **Framework**: FastAPI (Python 3.12)
*   **LLM**: Gemini 2.5-flash (Experimental) ผ่าน `google-genai` SDK
*   **Vector Database**: FAISS (Facebook AI Similarity Search)
*   **Embeddings**: BGE-M3 (BAAI/bge-m3) สำหรับการทำ Semantic Search ภาษาไทยที่แม่นยำ

---

## 📁 Project Structure

```text
├── app/                  # Next.js App Router (Frontend)
├── backend/              # FastAPI Server Logic
├── ai_core/              # AI Logic, RAG Engine, Gemini Client
│   ├── rag_engine.py     # ระบบค้นหาข้อมูลและ Vector Store
│   ├── gemini_client.py  # Agent Loop และ Function Calling
│   └── __init__.py       # Package Exports
├── public/               # Static assets & Data files
├── .env                  # Environment Variables (ต้องสร้างเอง)
├── run.py                # Script สำหรับรัน Backend
└── package.json          # Node.js dependencies
```

## 🧠 RAG Workflow & Technical Orchestration: "มัคจัง" Edition

ระบบของ **"มัคจัง"** ไม่ได้เป็นเพียงการดึงข้อมูลตามคำสำคัญ (Keyword Matching) แต่ทำงานบนสถาปัตยกรรม **Agentic RAG** ที่ใช้การตัดสินใจแบบ Real-time ผ่าน **Gemini 2.5-flash** และกลยุทธ์การดึงข้อมูลแบบผสมผสาน (Hybrid Retrieval) เพื่อผลลัพธ์ที่แม่นยำที่สุด

### 1. Intent Analysis & Context Awareness (ด่านวิเคราะห์เจตนา)
ก่อนการเริ่มค้นหา ระบบจะนำข้อความจากผู้ใช้เข้าสู่กระบวนการ **Context Enrichment** เพื่อสร้างความเข้าใจที่ลึกซึ้ง:
*   **Station Injection:** ระบบจะผนวก `selectedStation` จาก Frontend เข้าไปใน System Prompt แบบไดนามิก เพื่อสร้าง "กรอบความคิด" (Boundary) ให้ AI รับรู้ว่าผู้ใช้กำลังโฟกัสที่ย่านไหนเป็นพิเศษ
*   **Intent Classification:** ใช้เทคนิค **Few-shot Prompting** เพื่อจำแนกประเภทคำถามและเลือกเครื่องมือ (Tool) ที่เหมาะสม:
    *   **Greeting/Identity:** เรียกใช้ `_get_muek_jung_info` เพื่อแนะนำตัว
    *   **Direct Match:** ค้นหาด้วยชื่อสถานีหรือหมวดหมู่ (Exact Match)
    *   **Semantic Intent:** สำหรับคำถามเชิงอารมณ์หรือบรรยากาศ (เช่น "หาร้านนั่งชิลล์ถ่ายรูปสวย") จะส่งต่อไปยัง Semantic Search

---

### 2. Hybrid Retrieval Strategy (กลยุทธ์การดึงข้อมูลแบบผสมผสาน)
หัวใจของความแม่นยำในมัคจังคือการใช้ **Multi-Route Retrieval** เพื่อปิดจุดอ่อนของการค้นหาแบบ Vector เพียงอย่างเดียว:
*   **Metadata Filtering (Hard Constraints):** หากระบุสถานีหรือหมวดหมู่ชัดเจน ระบบจะกรองข้อมูลแบบ Exact Match เพื่อลด Noise และป้องกันปัญหา AI "หลอน" (Hallucination) ข้ามไปยังสถานีอื่นที่ไม่เกี่ยวข้อง
*   **Semantic Search (Neural Retrieval):** สำหรับคำถามที่มีความหมายซ่อนเร้น ระบบใช้โมเดล **BGE-M3** คำนวณค่าความคล้ายคลึงทางเวกเตอร์ (Cosine Similarity) ตามสูตร:
<img width="348" height="79" alt="Screenshot 2569-05-02 at 02 24 16" src="https://github.com/user-attachments/assets/5c14d861-92d6-4d16-8d85-aaad5a6ac99c" />

> **Technical Insight:** เทคนิคนี้ทำให้มัคจังเข้าใจว่าคำว่า *"ที่ทำงานเงียบๆ"* มีความหมายใกล้เคียงกับ *"Co-working space"* แม้จะไม่มีตัวอักษรที่ตรงกันเลยก็ตาม

---

### 3. Agentic Loop & Tool Calling (วงจรการคิดและการเลือกเครื่องมือ)
มัคจังทำงานในรูปแบบ **ReAct (Reason + Act) Pattern** เพื่อให้ได้คำตอบที่สมเหตุสมผลที่สุด:
*   **Reason:** AI พิจารณาประวัติการสนทนา (History) และ Context ปัจจุบันเพื่อวางแผนการหาคำตอบ
*   **Act:** ตัดสินใจเรียก Tool ผ่าน **Function Calling**
    *   ในรอบแรก (Step 0) ระบบจะถูกบังคับด้วย `mode="ANY"` เพื่อการันตีว่า AI จะต้องใช้ข้อมูลจริงจากเครื่องมือเท่านั้น
    *   **Multi-hop:** หากข้อมูลรอบแรกไม่เพียงพอ AI สามารถตัดสินใจเรียกเครื่องมืออื่นเพิ่มเติมได้เอง
*   **Observation:** AI ประเมินผลลัพธ์ที่ได้รับในรูปแบบ JSON เพื่อตรวจสอบความถูกต้องก่อนนำไปสรุปผล

---

### 4. Response Synthesis via AIDA Framework (การสรุปผลและปรับแต่งคำตอบ)
เมื่อได้ข้อมูลดิบ (Raw Data) ระบบจะเข้าสู่กระบวนการสังเคราะห์คำตอบเพื่อให้ "มัคจัง" ดูเป็นมิตรและกระตุ้นการท่องเที่ยวได้จริง:
*   **Data Grounding:** บังคับให้ AI ใช้ข้อมูลจาก `places_found` เท่านั้น ห้ามตอบนอกเหนือจากข้อเท็จจริงที่ค้นหาได้
*   **AIDA Framing:** ปรับโทนการสื่อสารตามโครงสร้างการตลาด:
    *   **A - Attention:** ทักทายด้วยน้ำเสียงที่สดใสและเปิดประเด็นให้น่าสนใจ
    *   **I - Interest:** ดึงไฮไลท์เด็ดของสถานที่ออกมานำเสนอ
    *   **D - Desire:** สร้างความรู้สึกอยากไป (เช่น แนะนำมุมถ่ายรูปหรือเมนูห้ามพลาด)
    *   **A - Action:** สรุปวิธีการเดินทางและแจ้ง **ทางออกสถานี (Exit)** ที่ชัดเจน

---

### 🛠 Tech Stack Summary
*   **LLM:** Gemini 2.5-flash
*   **Embedding Model:** BGE-M3
*   **Vector Logic:** FAISS (Facebook AI Similarity Search)
*   **Orchestration:** Custom Python Agent with Google GenAI SDK

---

## 🚀 Installation & Setup

### 1. Clone Project
```bash
git clone https://github.com/puz91/Thailand-Tourism-Mini-Hackathon---SuperAI.git
cd Thailand-Tourism-Mini-Hackathon---SuperAI
```

### 2. Environment Setup (.env)
สร้างไฟล์ `.env` ที่ Root Directory และใส่ค่าดังนี้:

```env
# Google Gemini API Key (รับได้ที่ Google AI Studio)
GEMINI_API_KEY=your_gemini_api_key_here

# Hugging Face Token (เพื่อความเร็วในการโหลด Embedding)
HF_TOKEN=your_huggingface_token_here

# Backend Configuration
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### 3. Backend Setup (Python)
แนะนำให้ใช้ Virtual Environment:
```bash
python -m venv venv
source venv/bin/activate  # สำหรับ Mac/Linux
# หรือ venv\Scripts\activate สำหรับ Windows

pip install -r requirements.txt
```

### 4. Frontend Setup (Node.js)
```bash
npm install
```

---

## 🏃 How to Run

คุณสามารถรันทั้ง Frontend และ Backend พร้อมกันได้ด้วยคำสั่งเดียว:

```bash
npm run dev:all
```

**หรือรันแยกส่วน:**
*   **Frontend**: `npm run dev` (Port 3000)
*   **Backend**: `python run.py` (Port 8000)

---

## 🧪 Testing the AI Core
หากต้องการทดสอบระบบ Agent Loop ผ่าน Terminal โดยตรง:
```bash
python test_ai_core.py --chat
```

---

## 🤝 Team 
โปรเจกต์นี้พัฒนาขึ้นเพื่อการแข่งขัน **Thailand Tourism Mini-Hackathon - SuperAI Season 6** 

---

**Note:** หากพบปัญหา `Failed to connect` หรือ `503 UNAVAILABLE` ให้ตรวจสอบการเชื่อมต่ออินเทอร์เน็ตและการ Restart `run.py` เพื่อโหลด API Key ตัวล่าสุดครับ

---


