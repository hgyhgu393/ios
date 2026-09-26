import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

# สร้างแอป FastAPI
app = FastAPI(
    title="Origin OS Update Server",
    description="API Server สำหรับตรวจสอบการอัปเดตระบบ Origin OS",
    version="1.0.0"
)

# ==========================================
# 1. ตั้งค่า CORS (เปิดให้แอป/เว็บเชื่อมต่อได้ ไม่ถูกเบราว์เซอร์บล็อก)
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # อนุญาตให้เข้าถึงได้จากทุก Domain / file:// / content://
    allow_credentials=True,
    allow_methods=["*"],        # อนุญาตทุก Method (GET, POST, HEAD ฯลฯ)
    allow_headers=["*"],        # อนุญาตทุก Header
)

# ==========================================
# 2. ฟังก์ชันอ่านไฟล์ update.txt
# ==========================================
def parse_update_file(file_path: str = "update.txt") -> dict:
    """
    ฟังก์ชันอ่านข้อมูลการอัปเดตจากไฟล์ update.txt
    """
    if not os.path.exists(file_path):
        return {
            "version": "1.0.0",
            "title": "ไม่พบไฟล์อัปเดต",
            "changelog": "ยังไม่มีรายละเอียดการอัปเดต",
            "download_url": ""
        }
    
    data = {}
    changelog_lines = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                
                # อ่านค่า Key: Value เช่น version: 2.0.0
                if ":" in line and not changelog_lines:
                    key, val = line.split(":", 1)
                    key_clean = key.strip().lower()
                    val_clean = val.strip()
                    
                    if key_clean in ["version", "title", "download_url", "url"]:
                        data[key_clean] = val_clean
                        continue
                
                # ถ้าเป็นบรรทัดรายละเอียดการอัปเดต
                changelog_lines.append(line.rstrip())

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return {
        "version": data.get("version", "1.0.0"),
        "title": data.get("title", "การอัปเดตระบบใหม่"),
        "changelog": "\n".join(changelog_lines) if changelog_lines else "ปรับปรุงประสิทธิภาพและเสถียรภาพของระบบ",
        "download_url": data.get("download_url", data.get("url", ""))
    }

# ==========================================
# 3. Endpoint หน้าแรก (ตรวจสอบสถานะเซิร์ฟเวอร์)
# ==========================================
@app.get("/")
@app.head("/")
def home():
    return {
        "status": "online",
        "message": "Origin OS Update Server is Running!"
    }

# ==========================================
# 4. Endpoint เช็กอัปเดต (/api/check-update)
# ==========================================
@app.get("/api/check-update")
def check_update(current_version: str = Query("1.0.0", description="เวอร์ชันปัจจุบันของแอปมือถือ")):
    update_info = parse_update_file("update.txt")
    latest_version = update_info.get("version", "1.0.0")

    # ตรวจสอบว่ามีเวอร์ชันใหม่กว่าหรือไม่
    has_update = (latest_version != current_version)

    return {
        "has_update": has_update,
        "current_version": current_version,
        "latest_version": latest_version,
        "title": update_info.get("title"),
        "changelog": update_info.get("changelog"),
        "download_url": update_info.get("download_url")
    }
