import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# อนุญาตให้เว็บจำลองมือถือเรียก API ได้จากทุกโดเมน (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def parse_update_file(file_path="update.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # อ่านเลขเวอร์ชันจาก *เลขเวอร์ชั่น*x.x.x*
        version_match = re.search(r'\*เลขเวอร์ชั่น\*(.*?)\*', content)
        version = version_match.group(1).strip() if version_match else "1.0.0"

        # อ่านคำอธิบายจาก [ ... ]
        changelog_match = re.search(r'\[(.*?)\]', content, re.DOTALL)
        changelog = changelog_match.group(1).strip() if changelog_match else ""

        # โค้ด JS จะอยู่หลังเครื่องหมาย ]
        js_code = ""
        if changelog_match:
            end_index = changelog_match.end()
            js_code = content[end_index:].strip()

        return {
            "version": version,
            "changelog": changelog,
            "code": js_code
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def home():
    return {"status": "Origin OS Update Server is Running!"}

@app.get("/api/check-update")
def check_update(current_version: str = "1.0.0"):
    data = parse_update_file("update.txt")
    
    if "error" in data:
        return {"has_update": False, "message": "Read error"}

    # ถ้าเลขเวอร์ชันในไฟล์ไม่ตรงกับเวอร์ชันปัจจุบันของผู้ใช้ ถือว่ามีอัปเดต
    if data["version"] != current_version:
        return {
            "has_update": True,
            "version": data["version"],
            "changelog": data["changelog"],
            "code": data["code"]
        }
    
    return {"has_update": False}
