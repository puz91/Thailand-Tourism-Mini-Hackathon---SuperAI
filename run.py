# run.py
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
load_dotenv()

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.api:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        # เพิ่มบรรทัดนี้เพื่อข้าม venv และไฟล์ขยะอื่นๆ
        reload_excludes=["venv/*", ".next/*", "__pycache__/*", "*.log"] 
    )