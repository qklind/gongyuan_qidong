import os
import sys
import uuid
import base64
from datetime import datetime
from typing import Optional, Dict, Any

# ============================================================
#  Friendly dependency guard - avoids confusing stack traces
#  Test ALL imports here first, show ONE-LINE fix, not a traceback.
# ============================================================
_MISSING_DEPS_HINT = None
try:
    import fastapi
    import pydantic
    import starlette
    import PIL
    import cv2
    import numpy
    # explicitly import multipart BEFORE FastAPI registers UploadFile routes.
    # NOTE: pip package name is "python-multipart" but import name is "multipart"!
    # FastAPI internally checks the same "multipart" module.
    import multipart
    from film_library import FILMS, match_film_by_keywords
    from image_processor import apply_film_filter
    from fastapi import FastAPI, UploadFile, File, HTTPException, Form
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import JSONResponse, FileResponse
    from pydantic import BaseModel
except ModuleNotFoundError as _e:
    _pkg_name = getattr(_e, 'name', None) or str(_e)
    if _pkg_name.lower() == 'multipart' or 'multipart' in _pkg_name.lower():
        _MISSING_DEPS_HINT = f"""
============================================================
 🛑  缺少 fastapi 文件上传必需依赖：multipart（pip包名 python-multipart）
============================================================
 请粘贴这一行命令回车（0.5MB，几秒钟装完）：

 python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn python-multipart

 或者装完整全家桶（推荐，后续不再撞缺包坑）：

 python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt

 然后重新运行：  python main.py
============================================================"""
    else:
        _MISSING_DEPS_HINT = f"""
============================================================
 🛑  缺少依赖模块：{_pkg_name}
============================================================
 请在 backend 目录下粘贴这一行命令回车（同一个解释器装，100%不会装错位置）：

 python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn -r requirements.txt

 装完重新运行：  python main.py
============================================================"""
except RuntimeError as _e:
    _msg = str(_e).lower()
    if 'multipart' in _msg:
        _MISSING_DEPS_HINT = f"""
============================================================
 🛑  FastAPI 报告缺少 python-multipart
============================================================
 请粘贴这一行命令回车：

 python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn python-multipart

 装完重新运行：  python main.py
============================================================"""
    else:
        raise

if _MISSING_DEPS_HINT is not None:
    print(_MISSING_DEPS_HINT)
    sys.exit(4)


def _resolve_base_dir() -> str:
    """
    Compatible with both raw-source run AND PyInstaller one-file/one-dir build.
    - Source run: use directory of this .py file
    - PyInstaller build: use directory of the running .exe
    """
    if getattr(sys, "frozen", False):
        # Running from PyInstaller build - exe dir contains data folders
        # sys.executable points to launcher .exe, its folder is the bundle root
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BACKEND_DIR = _resolve_base_dir()
BASE_DIR = BACKEND_DIR
# When frozen, folders (frontend/uploads/outputs) live next to the .exe.
# When in source, backend is a subfolder and frontend is one level up.
if getattr(sys, "frozen", False):
    UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")
    OUTPUT_DIR = os.path.join(BACKEND_DIR, "outputs")
    FRONTEND_DIR = os.path.join(BACKEND_DIR, "frontend")
    # try bundled internal film_library / image_processor dirs first
    if not os.path.isdir(FRONTEND_DIR):
        FRONTEND_DIR = os.path.join(os.path.dirname(sys.executable), "_internal", "frontend")
else:
    UPLOAD_DIR = os.path.join(BACKEND_DIR, "uploads")
    OUTPUT_DIR = os.path.join(BACKEND_DIR, "outputs")
    FRONTEND_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "frontend")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
ASSETS_DIR = os.path.join(BACKEND_DIR, "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

app = FastAPI(
    title="公元胶片模拟器 API",
    description="公元胶片博物馆智能图像滤镜服务",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class MatchRequest(BaseModel):
    text: str


class ProcessRequest(BaseModel):
    image_base64: str
    film_id: str
    custom_params: Optional[Dict[str, Any]] = None


class ProcessUrlRequest(BaseModel):
    image_url: str
    film_id: str


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "service": "公元胶片模拟器",
        "films_available": len(FILMS),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/films")
async def list_films():
    films_list = []
    for fid, film in FILMS.items():
        films_list.append({
            "id": film["id"],
            "name": film["name"],
            "era": film["era"],
            "category": film["category"],
            "keywords": film["keywords"],
            "story_title": film["story"]["title"],
            "story_content": film["story"]["content"],
            "fun_fact": film["story"]["fun_fact"]
        })
    return {"films": films_list}


@app.get("/api/films/{film_id}")
async def get_film(film_id: str):
    if film_id not in FILMS:
        raise HTTPException(status_code=404, detail=f"胶片 {film_id} 不存在")
    film = FILMS[film_id]
    return {
        "id": film["id"],
        "name": film["name"],
        "era": film["era"],
        "category": film["category"],
        "keywords": film["keywords"],
        "filter_params": film["filter_params"],
        "story": film["story"]
    }


@app.post("/api/match")
async def match_film(req: MatchRequest):
    film_id = match_film_by_keywords(req.text)
    film = FILMS[film_id]
    return {
        "matched_film_id": film_id,
        "matched_film_name": film["name"],
        "confidence_keywords": [kw for kw in film["keywords"] if kw.lower() in req.text.lower()],
        "film": {
            "id": film["id"],
            "name": film["name"],
            "era": film["era"],
            "category": film["category"],
            "keywords": film["keywords"],
            "story_title": film["story"]["title"],
            "story_content": film["story"]["content"],
            "fun_fact": film["story"]["fun_fact"]
        }
    }


@app.post("/api/process/upload")
async def process_upload(
    file: UploadFile = File(...),
    film_id: str = Form(...)
):
    if film_id not in FILMS:
        raise HTTPException(status_code=400, detail=f"胶片 {film_id} 不存在")
    try:
        contents = await file.read()
        film = FILMS[film_id]
        params = film["filter_params"]

        processed = apply_film_filter(contents, params)

        job_id = uuid.uuid4().hex[:12]
        orig_ext = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
        orig_name = f"{job_id}_orig{orig_ext}"
        out_name = f"{job_id}_processed.jpg"

        orig_path = os.path.join(UPLOAD_DIR, orig_name)
        out_path = os.path.join(OUTPUT_DIR, out_name)

        with open(orig_path, "wb") as f:
            f.write(contents)
        with open(out_path, "wb") as f:
            f.write(processed)

        orig_b64 = base64.b64encode(contents).decode("utf-8")
        out_b64 = base64.b64encode(processed).decode("utf-8")

        return {
            "success": True,
            "job_id": job_id,
            "film": {
                "id": film["id"],
                "name": film["name"],
                "era": film["era"],
                "category": film["category"]
            },
            "original": {
                "filename": orig_name,
                "url": f"/uploads/{orig_name}",
                "base64": orig_b64
            },
            "processed": {
                "filename": out_name,
                "url": f"/outputs/{out_name}",
                "base64": out_b64
            },
            "story": film["story"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图像处理失败: {str(e)}")


@app.post("/api/process/base64")
async def process_base64(req: ProcessRequest):
    if req.film_id not in FILMS:
        raise HTTPException(status_code=400, detail=f"胶片 {req.film_id} 不存在")
    try:
        image_data = req.image_base64
        if "," in image_data:
            image_data = image_data.split(",")[1]
        contents = base64.b64decode(image_data)

        film = FILMS[req.film_id]
        params = req.custom_params or film["filter_params"]

        processed = apply_film_filter(contents, params)

        job_id = uuid.uuid4().hex[:12]
        out_b64 = base64.b64encode(processed).decode("utf-8")

        return {
            "success": True,
            "job_id": job_id,
            "film": {
                "id": film["id"],
                "name": film["name"],
                "era": film["era"],
                "category": film["category"]
            },
            "processed": {
                "base64": out_b64,
                "mime_type": "image/jpeg"
            },
            "story": film["story"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"图像处理失败: {str(e)}")


@app.post("/api/batch/preview")
async def batch_preview(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        results = []
        for fid, film in FILMS.items():
            processed = apply_film_filter(contents, film["filter_params"])
            out_b64 = base64.b64encode(processed).decode("utf-8")
            results.append({
                "film_id": fid,
                "film_name": film["name"],
                "category": film["category"],
                "thumbnail_base64": out_b64
            })
        return {"success": True, "previews": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量预览失败: {str(e)}")


app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

FRONTEND_INDEX = os.path.join(FRONTEND_DIR, "index.html")
FRONTEND_MOUNTED = False

if os.path.isdir(FRONTEND_DIR) and os.path.isfile(FRONTEND_INDEX):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
    FRONTEND_MOUNTED = True
else:
    print(f"  [WARN] Frontend directory or index.html NOT found at:")
    print(f"         Expected dir : {FRONTEND_DIR}")
    print(f"         Expected index: {FRONTEND_INDEX}")
    print(f"         -> Fallback hint page mounted on '/' instead (API still works).")
    print(f"         -> Open frontend via file:// only works after you start the API and set API_BASE.")

    FALLBACK_HTML = f"""<!doctype html><html><head><meta charset="utf-8">
<title>公元胶片模拟器 · API服务已运行</title>
<style>
body{{margin:0;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#1a1410;color:#e8dcc4;}}
.wrap{{max-width:720px;margin:60px auto;padding:32px;}}
h1{{color:#e9c46a;margin:0 0 16px;font-weight:600;}}
.ok{{color:#6abf69;font-weight:700;}}
.warn{{color:#e76f51;}}
.card{{background:#2a1f18;border:1px solid #4a3523;border-radius:14px;padding:22px;margin:22px 0;line-height:1.8;}}
code{{background:#3d2c1f;padding:3px 8px;border-radius:6px;color:#f4d9a0;font-size:14px;}}
a.btn{{display:inline-block;margin-top:8px;padding:12px 20px;background:#b8860b;color:#1a1410;font-weight:700;
text-decoration:none;border-radius:10px;}}a.btn:hover{{background:#e9c46a;}}
.links a{{color:#e9c46a;}}
</style></head><body>
<div class="wrap">
<h1>🎞️  公元胶片模拟器 · API服务 <span class="ok">运行中</span></h1>
<div class="card">
<div class="warn">⚠️ 前端 HTML 页面 <b>没有自动挂载</b>。原因：找不到前端目录。</div>
<p><b>正确的打开方式（推荐）：</b></p>
<ol>
<li>关闭本页面。</li>
<li>直接在浏览器里打开你的前端文件所在路径下的 <code>frontend/index.html</code>（通过文件管理器双击打开也行，只要看到页面就好）。</li>
<li>或者：把 <code>frontend/</code> 目录移动/复制到后端程序能识别的位置：
<br>&nbsp;&nbsp;Expected frontend dir = <code>{FRONTEND_DIR}</code>
<br>&nbsp;&nbsp;Expected index.html   = <code>{FRONTEND_INDEX}</code>
</li>
</ol>
<p><b>如果你已经能在另一个标签页里看到前端界面（胶片卡片）：</b><br>
点击冲印提示"请先启动后端"是因为前端是 file:// 协议打开的，fetch 默认被浏览器禁止跨 file/localhost。修复两种方法（任选其一）：
<br>① 把前端部署到本服务的 <code>{FRONTEND_DIR}</code> 下 → 然后访问 <code>http://localhost:8000/</code>
<br>② 先保持现在 file:// 打开，然后前端界面右上角会弹出横幅，按照横幅提示点一下"自动切换 API_BASE 到 localhost:8000"按钮即可。
</p>
</div>

<div class="card links">
<h3>✅ API 入口验证链接（点一下应该返回JSON）：</h3>
<ul>
<li><a href="/api/health" target="_blank">/api/health — 健康检查</a></li>
<li><a href="/api/films" target="_blank">/api/films — 8款胶片列表</a></li>
<li><a href="/docs" target="_blank">/docs — FastAPI自动文档</a></li>
</ul>
<a class="btn" href="/api/health">👉 先点这里验证 API 是否活着</a>
</div>

</div></body></html>"""

    @app.get("/", include_in_schema=False)
    async def root_fallback():
        from fastapi.responses import HTMLResponse
        return HTMLResponse(FALLBACK_HTML)


@app.on_event("startup")
def _startup_checks():
    import sys as _sys
    print("-" * 65)
    print("  Pre-flight checks:")
    print(f"   - Python      : {_sys.version.split()[0]}")
    print(f"   - BACKEND_DIR : {BACKEND_DIR}")
    print(f"   - UPLOAD_DIR  : {UPLOAD_DIR}  [{os.path.isdir(UPLOAD_DIR)}]")
    print(f"   - OUTPUT_DIR  : {OUTPUT_DIR}  [{os.path.isdir(OUTPUT_DIR)}]")
    print(f"   - FRONTEND_DIR: {FRONTEND_DIR}")
    print(f"                 exists folder? [{os.path.isdir(FRONTEND_DIR)}]  has index.html? [{os.path.isfile(FRONTEND_INDEX)}]")
    print(f"   - Frontend mounted: [{FRONTEND_MOUNTED}]")
    print("-" * 65)
    print("  🛑 WAIT for the line below before opening browser:")
    print("     Uvicorn running on http://0.0.0.0:8000  ← server is ready")
    print("-" * 65)


if __name__ == "__main__":
    import uvicorn
    import socket

    def get_lan_ips():
        ips = []
        try:
            hostname = socket.gethostname()
            # 先尝试主机名解析
            for info in socket.getaddrinfo(hostname, None, family=socket.AF_INET):
                ip = info[4][0]
                if ip.startswith("127."):
                    continue
                if ip not in ips:
                    ips.append(ip)
        except Exception:
            pass
        # 再兜底：枚举所有网卡
        try:
            import subprocess
            import re
            out = subprocess.check_output(["ipconfig"], text=True, errors="ignore")
            for m in re.finditer(r"IPv4.*?:\s*([0-9.]+)", out):
                ip = m.group(1)
                if ip.startswith("169.254."):
                    continue
                if ip.startswith("127."):
                    continue
                if ip not in ips:
                    ips.append(ip)
        except Exception:
            pass
        return ips

    lan_ips = get_lan_ips()

    print("=" * 65)
    print(" 🎞️  Gongyuan Film Simulator - Digital Darkroom Server Starting")
    print("=" * 65)
    print(f" 📁 Upload dir : {UPLOAD_DIR}")
    print(f" 📁 Output dir : {OUTPUT_DIR}")
    print(f" 📁 Frontend   : {FRONTEND_DIR} ({'Mounted' if os.path.exists(FRONTEND_DIR) else 'Not found'})")
    print(f" 🎬 Films loaded: {len(FILMS)}")
    for fid, film in FILMS.items():
        print(f"      - {film['short_name']:8s} [{fid}] {film['era']}")
    print("-" * 65)
    print("  ✅ This Machine   :")
    print(f"       http://localhost:8000/")
    print(f"       http://127.0.0.1:8000/")
    if lan_ips:
        print("  🌐 LAN / Other PCs (same WiFi or network):")
        for ip in lan_ips:
            print(f"       http://{ip}:8000/")
    print("-" * 65)
    print("  Docs    : http://localhost:8000/docs")
    print("  Health  : http://localhost:8000/api/health")
    print("  Films   : http://localhost:8000/api/films")
    print("=" * 65)
    print("  Tip: Close this window to stop the server.")
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000)
