import os
import json
import shutil
from fastapi import FastAPI, Request, Form, File, UploadFile, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Origin OS Update & Admin Server",
    version="3.0.0"
)

# ==========================================
# 1. ตั้งค่า CORS (เปิดให้แอป/เว็บทุกแห่งเชื่อมต่อได้)
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. ตั้งค่าโฟลเดอร์เก็บไฟล์อัปโหลด & โฟลเดอร์ Static
# ==========================================
UPLOAD_DIR = "uploads"
DATA_FILE = "update_data.json"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# เปิดไดเรกทอรีให้อ่านไฟล์ดาวน์โหลดผ่านเว็บได้ เช่น /uploads/filename.js
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


def load_update_data():
    """ฟังก์ชันอ่านข้อมูลอัปเดตล่าสุด"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "version": "1.0.0",
        "title": "ระบบเป็นเวอร์ชันล่าสุดแล้ว",
        "changelog": "ไม่มีรายการอัปเดตในขณะนี้",
        "download_url": "",
        "filename": ""
    }


def save_update_data(data):
    """ฟังก์ชันบันทึกข้อมูลอัปเดตลงไฟล์ JSON"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ==========================================
# 3. Endpoints ระบบ
# ==========================================

@app.get("/")
@app.head("/")
def home():
    return {"status": "online", "message": "Origin OS Update Server is Running!"}


# ------------------------------------------
# หน้าแอดมินสำหรับจัดการการอัปเดต (/a1234)
# ------------------------------------------
@app.get("/a1234", response_class=HTMLResponse)
def admin_page(request: Request):
    current = load_update_data()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Origin OS - ระบบจัดการการอัปเดต (Admin)</title>
        <link href="https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;500;600&display=swap" rel="stylesheet">
        <style>
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: 'Prompt', sans-serif;
            }}
            body {{
                background-color: #0f172a;
                color: #f8fafc;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }}
            .card {{
                background: #1e293b;
                border-radius: 20px;
                padding: 28px;
                width: 100%;
                max-width: 500px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                border: 1px solid #334155;
            }}
            h2 {{
                color: #38bdf8;
                font-weight: 600;
                margin-bottom: 6px;
                text-align: center;
            }}
            p.subtitle {{
                color: #94a3b8;
                font-size: 0.88em;
                text-align: center;
                margin-bottom: 20px;
            }}
            .status-box {{
                background: #0f172a;
                border-radius: 12px;
                padding: 14px;
                margin-bottom: 20px;
                border-left: 4px solid #38bdf8;
                font-size: 0.85em;
                line-height: 1.6;
            }}
            .status-box strong {{
                color: #38bdf8;
            }}
            .form-group {{
                margin-bottom: 16px;
            }}
            label {{
                display: block;
                margin-bottom: 6px;
                font-size: 0.88em;
                color: #cbd5e1;
            }}
            input[type="text"], textarea, input[type="file"] {{
                width: 100%;
                padding: 12px;
                background: #0f172a;
                border: 1px solid #334155;
                border-radius: 10px;
                color: #fff;
                font-size: 0.9em;
                outline: none;
                transition: border-color 0.2s;
            }}
            input[type="text"]:focus, textarea:focus {{
                border-color: #38bdf8;
            }}
            textarea {{
                resize: vertical;
                min-height: 90px;
            }}
            input[type="file"] {{
                padding: 8px;
                cursor: pointer;
            }}
            .btn-submit {{
                width: 100%;
                padding: 14px;
                background: linear-gradient(135deg, #0284c7, #2563eb);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 0.98em;
                font-weight: 600;
                cursor: pointer;
                transition: transform 0.1s, opacity 0.2s;
                margin-top: 8px;
            }}
            .btn-submit:hover {{
                opacity: 0.9;
            }}
            .btn-submit:active {{
                transform: scale(0.98);
            }}
            .alert {{
                padding: 12px;
                border-radius: 10px;
                margin-top: 16px;
                display: none;
                font-size: 0.88em;
                text-align: center;
            }}
            .alert-success {{
                background: rgba(34, 197, 94, 0.2);
                color: #4ade80;
                border: 1px solid #22c55e;
            }}
            .alert-error {{
                background: rgba(239, 68, 68, 0.2);
                color: #f87171;
                border: 1px solid #ef4444;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>⚙️ Origin OS Admin Panel</h2>
            <p class="subtitle">ระบบจัดการอัปเดตซอฟต์แวร์</p>

            <div class="status-box">
                <div><strong>เวอร์ชันปัจจุบัน:</strong> <span id="currentVer">{current.get('version')}</span></div>
                <div><strong>หัวข้ออัปเดต:</strong> {current.get('title')}</div>
                <div><strong>ไฟล์แนบ:</strong> {current.get('filename') if current.get('filename') else 'ไม่มีไฟล์'}</div>
            </div>

            <form id="updateForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label>1. เลขเวอร์ชัน (Version)</label>
                    <input type="text" id="version" name="version" placeholder="เช่น 3.0.0" value="{current.get('version')}" required>
                </div>

                <div class="form-group">
                    <label>2. หัวข้อการอัปเดต (Title)</label>
                    <input type="text" id="title" name="title" placeholder="เช่น การอัปเดตระบบ Origin OS v3.0.0" value="{current.get('title')}" required>
                </div>

                <div class="form-group">
                    <label>3. คำอธิบาย / รายละเอียดการอัปเดต (Changelog)</label>
                    <textarea id="changelog" name="changelog" placeholder="- รายละเอียดฟีเจอร์ใหม่\n- แก้ไขบั๊ก\n(หรือวางโค้ด JS ที่นี่)" required>{current.get('changelog')}</textarea>
                </div>

                <div class="form-group">
                    <label>4. อัปโหลดไฟล์อัปเดตจากเครื่อง (Optional)</label>
                    <input type="file" id="file" name="file">
                </div>

                <button type="submit" class="btn-submit" id="btnSubmit">🚀 ส่งการอัปเดต</button>
            </form>

            <div id="alertBox" class="alert"></div>
        </div>

        <script>
            document.getElementById('updateForm').addEventListener('submit', async (e) => {{
                e.preventDefault();
                const btn = document.getElementById('btnSubmit');
                const alertBox = document.getElementById('alertBox');

                btn.disabled = true;
                btn.innerText = "⏳ กำลังอัปโหลดและบันทึก...";
                alertBox.style.display = "none";

                const formData = new FormData(e.target);

                try {{
                    const response = await fetch('/api/admin/update', {{
                        method: 'POST',
                        body: formData
                    }});

                    const result = await response.json();

                    if (response.ok) {{
                        alertBox.className = "alert alert-success";
                        alertBox.innerText = "✅ " + result.message;
                        alertBox.style.display = "block";
                        document.getElementById('currentVer').innerText = result.data.version;
                    }} else {{
                        throw new Error(result.detail || "เกิดข้อผิดพลาดในการบันทึก");
                    }}
                }} catch (err) {{
                    alertBox.className = "alert alert-error";
                    alertBox.innerText = "❌ " + err.message;
                    alertBox.style.display = "block";
                }} finally {{
                    btn.disabled = false;
                    btn.innerText = "🚀 ส่งการอัปเดต";
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# ------------------------------------------
# API รับข้อมูลบันทึกการอัปเดตจากหน้าแอดมิน
# ------------------------------------------
@app.post("/api/admin/update")
async def process_admin_update(
    request: Request,
    version: str = Form(...),
    title: str = Form(...),
    changelog: str = Form(...),
    file: UploadFile = File(None)
):
    current_data = load_update_data()
    clean_version = version.lower().replace("v", "").strip()
    
    download_url = current_data.get("download_url", "")
    filename = current_data.get("filename", "")

    # ถ้ามีการอัปโหลดไฟล์ใหม่เข้ามา
    if file and file.filename:
        filename = file.filename
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # บันทึกไฟล์ลงโฟลเดอร์ uploads
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # สร้าง URL สำหรับดาวน์โหลดไฟล์ตรงๆ
        base_url = str(request.base_url).rstrip("/")
        download_url = f"{base_url}/uploads/{filename}"

    new_data = {
        "version": clean_version,
        "title": title.strip(),
        "changelog": changelog.strip(),
        "download_url": download_url,
        "filename": filename
    }

    save_update_data(new_data)

    return {
        "status": "success",
        "message": f"ปล่อยการอัปเดตเวอร์ชัน {clean_version} สำเร็จเรียบร้อย!",
        "data": new_data
    }


# ------------------------------------------
# API สำหรับแอปมือถือจำลองเรียกตรวจเช็กอัปเดต
# ------------------------------------------
@app.get("/api/check-update")
def check_update(current_version: str = Query("1.0.0")):
    data = load_update_data()
    latest_ver = data.get("version", "1.0.0")
    user_ver = current_version.lower().replace("v", "").strip()

    has_update = (latest_ver != user_ver)

    return {
        "has_update": has_update,
        "current_version": current_version,
        "latest_version": latest_ver,
        "title": data.get("title"),
        "changelog": data.get("changelog"),
        "download_url": data.get("download_url")
    }
