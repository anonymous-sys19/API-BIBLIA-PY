#!/usr/bin/env python3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app
from app.db.models import GuiaEstudio
from fastapi.testclient import TestClient

client = TestClient(app)

GUIA_PATH = Path.home() / "Escritorio" / "Guia.md"

if not GUIA_PATH.exists():
    print(f"Error: {GUIA_PATH} no encontrado")
    sys.exit(1)

content = GUIA_PATH.read_text(encoding="utf-8")

payload = GuiaEstudio(
    id=None,
    title="Guía de Estudio Bíblico Integral: De 0 a 100 con Propósito",
    author="Un teólogo, historiador bíblico y pastor con décadas de experiencia en discipulado cristiano",
    content=content,
    tags="discipulado, fe, oracion, gracia, santidad, espiritu-santo, profecia, amor, evangelismo, misiones",
    status="published",
)

resp = client.post("/guide/add", json=payload.__dict__)
if resp.status_code == 200:
    data = resp.json()
    print(f"Guía creada exitosamente con ID: {data.get('id')}")
else:
    print(f"Error: {resp.status_code} - {resp.text}")
    sys.exit(1)
