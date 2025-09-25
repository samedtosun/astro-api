# main.py
from fastapi import FastAPI, Form, HTTPException, Header
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from kerykeion import AstrologicalSubject, KerykeionSvg
import os
import tempfile
import logging

# Log seviyesini düşür
logging.getLogger("kerykeion").setLevel(logging.WARNING)

app = FastAPI(title="Gizli Doğum Haritası API")

# CORS: Flutter mobile için gerekli
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gizli API anahtarı (Render'da ayarlanacak)
SECRET_API_KEY = os.getenv("API_KEY", "default-secret-key-for-local-testing")

@app.get("/")
def home():
    return {"status": "OK", "message": "Bu API sadece yetkili kullanıcılar içindir."}

@app.post("/generate_chart")
async def generate_chart(
    api_key: str = Header(None, alias="X-API-Key"),
    name: str = Form("Kullanıcı"),
    year: int = Form(...),
    month: int = Form(...),
    day: int = Form(...),
    hour: int = Form(...),
    minute: int = Form(...),
    city: str = Form(...),
    nation: str = Form("TR")
):
    if api_key != SECRET_API_KEY:
        raise HTTPException(status_code=403, detail="Erişim reddedildi")
    
    try:
        person = KrInstance(name, year, month, day, hour, minute, city, nation)
        with tempfile.TemporaryDirectory() as tmpdir:
            svg = MakeSvgInstance(person, chart_type="Natal", new_output_directory=tmpdir)
            svg.makeSVG()
            file_path = os.path.join(tmpdir, svg.output_filename)
            
            if not os.path.exists(file_path):
                raise HTTPException(status_code=500, detail="SVG oluşturulamadı")
            
            with open(file_path, "r", encoding="utf-8") as f:
                svg_content = f.read()
            
            return Response(content=svg_content, media_type="image/svg+xml")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Hata: {str(e)}")