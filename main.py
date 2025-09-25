from fastapi import FastAPI, Form, HTTPException, Header
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from kerykeion.core import AstrologicalSubject
from kerykeion.svg_classes import KerykeionSvg
import os
import tempfile
import logging

logging.getLogger("kerykeion").setLevel(logging.WARNING)

app = FastAPI(title="Gizli Doğum Haritası API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_API_KEY = os.getenv("API_KEY", "test-key")

@app.get("/")
def home():
    return {"status": "OK", "message": "API çalışıyor."}

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
        raise HTTPException(status_code=403, detail="Geçersiz API anahtarı")
    
    try:
        person = AstrologicalSubject(
            name=name,
            year=year,
            month=month,
            day=day,
            hour=hour,
            minute=minute,
            city=city,
            nation=nation
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            svg = KerykeionSvg(
                person,
                chart_type="Natal",
                new_output_directory=tmpdir
            )
            svg.make_svg()
            file_path = svg.output_filepath
            
            with open(file_path, "r", encoding="utf-8") as f:
                svg_content = f.read()
            
            return Response(content=svg_content, media_type="image/svg+xml")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Hata: {str(e)}")