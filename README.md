

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


