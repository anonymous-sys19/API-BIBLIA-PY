import logging
import re
import os
from datetime import datetime
from contextlib import asynccontextmanager

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional

from app.db.database import BibliaEngine, StreamManager, VideoManager
from app.db.models import RadioStream, Video, normalizar, BIBLIAS_VERSIONES
from app.db.ws_manager import ConnectionManager
from app.files.doc.doc import doc_api_json

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando GhostRoot Bible API")
    yield
    logger.info("Cerrando GhostRoot Bible API")

app = FastAPI(
    title="GhostRoot Bible API",
    version="1.0.0",
    description="API para gestión y exploración de las Sagradas Escrituras",
    lifespan=lifespan
)

BIBLIAS = BIBLIAS_VERSIONES()
engine = BibliaEngine(BIBLIAS)

TURSO_DB_URL = os.getenv("TURSO_DB_URL", "")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

stream_engine = StreamManager(TURSO_DB_URL, TURSO_AUTH_TOKEN)
video_engine = VideoManager(TURSO_DB_URL, TURSO_AUTH_TOKEN)

ws_manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False
)

ADMIN_UI_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "admin-ui")
app.mount("/admin/static", StaticFiles(directory=ADMIN_UI_PATH), name="admin-static")

DOCS_UI_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "docs-ui")
app.mount("/docs/static", StaticFiles(directory=DOCS_UI_PATH), name="docs-static")

STATIC_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=STATIC_PATH), name="static")

@app.get("/", tags=["Documentation"])
def docs_ui():
    """Documentación formal de la API"""
    return FileResponse(os.path.join(DOCS_UI_PATH, "index.html"))

@app.get("/api-info", tags=["Info"])
def api_info():
    """Información JSON de la API"""
    return doc_api_json(BIBLIAS)

@app.get("/admin", tags=["Admin"])
def admin_ui():
    return FileResponse(os.path.join(ADMIN_UI_PATH, "index.html"))

@app.get("/download/skill", tags=["Docs"])
def download_skill():
    return FileResponse(
        os.path.join(STATIC_PATH, "SKILL.md"),
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=ghostroot-bible-api-skill.md"}
    )

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/", tags=["Docs"])
def home():
    """Información base de la API. tipo documentación interactiva"""
    return doc_api_json(BIBLIAS)  

@app.get("/daily")
def daily():
    """Endpoint del pasaje bíblico diario[cite: 1]."""
    return engine.get_pasaje_diario()

@app.get("/daily/{version}")
def daily_with_version(version: Optional[str] = None):
    """Endpoint del pasaje bíblico diario con versión especificada[cite: 1]."""
    return engine.get_pasaje_diario(version)

@app.get("/list/testaments")
def list_testaments(version: Optional[str] = None):
    """Lista los testamentos disponibles."""
    return engine.obtener_testamentos(version)

@app.get("/list/books")
def list_books(version: Optional[str] = None, testament: Optional[int] = None):
    """Lista todos los libros o filtra por ID de testamento (1:Antiguo, 2:Nuevo)."""
    return engine.obtener_libros(version, testament)

@app.get("/list/books/antiguo")
def list_old_testament(version: Optional[str] = None):
    """Acceso rápido al Antiguo Testamento."""
    return engine.obtener_libros(version, testament_id=1)

@app.get("/list/books/nuevo")
def list_new_testament(version: Optional[str] = None):
    """Acceso rápido al Nuevo Testamento."""
    return engine.obtener_libros(version, testament_id=2)

@app.get("/info/chapters/{libro_id}")
def get_chapters_count(libro_id: int, version: Optional[str] = None):
    return {"total": engine.obtener_cantidad_capitulos(libro_id, version)}

@app.get("/info/verses/{libro_id}/{chapter}")
def get_verses_count(libro_id: int, chapter: int, version: Optional[str] = None):
    return {"total": engine.obtener_cantidad_versiculos(libro_id, chapter, version)}

# --- LÓGICA DE RUTAS DINÁMICAS ---

def buscar_libro_id(nombre: str, version: Optional[str] = None) -> int:
    """Busca el ID del libro ignorando tildes y mayúsculas[cite: 1]."""
    libros = engine.obtener_libros(version)
    nombre_norm = normalizar(nombre)
    for l in libros:
        if normalizar(l['name']) == nombre_norm or normalizar(l['abbreviation']) == nombre_norm:
            return l['id']
    raise HTTPException(status_code=404, detail=f"Libro '{nombre}' no encontrado")

@app.get("/search/{query}")
def search(query: str, version: Optional[str] = None):
    """
    Ahora acepta 'amor al projimo' y encontrará '...amó al prójimo...'[cite: 1, 2].
    """
    # Limpiamos posibles espacios extra al inicio o final
    query_limpia = query.strip()
    
    if not query_limpia:
        return []
        
    resultados = engine.buscar_texto(query_limpia, version)
    return {
        "busqueda": query_limpia,
        "cantidad": len(resultados),
        "resultados": resultados
    }
@app.get("/{libro}/{capitulo}")
def get_chapter(libro: str, capitulo: int, version: Optional[str] = None):
    """Endpoint juan/1 -> Retorna capítulo completo[cite: 1, 2]."""
    l_id = buscar_libro_id(libro, version)
    return engine.get_capitulo(l_id, capitulo, version)

@app.get("/bible/{book_id}/{chapter}")
def get_chapter_by_id(book_id: int, chapter: int, version: Optional[str] = None):
    """Retorna capítulo completo por ID de libro."""
    return engine.get_capitulo(book_id, chapter, version)

@app.get("/{libro}/{capitulo}/{versiculo}")
@app.get("/{libro}/{capitulo}/{versiculo}/{version}")
def get_verse(libro: str, capitulo: int, versiculo: int, version: Optional[str] = None):
    """Endpoint juan/3/16 -> Retorna un verso[cite: 1, 2]."""
    l_id = buscar_libro_id(libro, version)
    res = engine.get_verso(l_id, capitulo, versiculo, version)
    if not res: raise HTTPException(status_code=404)
    return res


# --- WEBSOCKETS EN TIEMPO REAL ---

allowed_ws_channels = {"videos", "streams", "biblia"}

@app.websocket("/ws/{channel}")
async def ws_realtime(ws: WebSocket, channel: str):
    if channel not in allowed_ws_channels:
        await ws.close(code=4004, reason=f"Canal no válido: {channel}")
        return
    await ws_manager.connect(channel, ws)
    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(channel, ws)

# --- RUTAS DE RADIO STREAMING ---


@app.get("/stream", tags=["Streaming"])
def listar_radios():
    return stream_engine.listar_radios()

@app.post("/stream/add", tags=["Streaming"])
async def nueva_radio(radio: RadioStream):
    radio_id = stream_engine.agregar_radio(radio)
    if not radio_id:
        raise HTTPException(status_code=400, detail="Error al agregar radio")
    await ws_manager.broadcast("streams", {
        "type": "stream:created",
        "data": {**radio.__dict__, "id": radio_id}
    })
    return {"status": "success", "id": radio_id, "mensaje": "Radio agregada"}

@app.delete("/stream/{radio_id}", tags=["Streaming"])
async def borrar_radio(radio_id: int):
    if stream_engine.eliminar_radio(radio_id):
        await ws_manager.broadcast("streams", {
            "type": "stream:deleted",
            "data": {"id": radio_id}
        })
        return {"mensaje": "Radio eliminada"}
    raise HTTPException(status_code=404, detail="No se encontró la radio")

@app.put("/stream/{radio_id}", tags=["Streaming"])
async def editar_radio(radio_id: int, radio: RadioStream):
    if stream_engine.editar_radio(radio_id, radio):
        await ws_manager.broadcast("streams", {
            "type": "stream:updated",
            "data": {**radio.__dict__, "id": radio_id}
        })
        return {"mensaje": "Radio actualizada"}
    raise HTTPException(status_code=404, detail="No se encontró la radio")

# --- RUTAS DE VIDEO STREAMING ---

def detect_url_type(url: str) -> dict:
    """Detecta si una URL es de YouTube o Spotify y devuelve tipo e ID."""
    youtube_regex = r"(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([0-9A-Za-z_-]{11})"
    match = re.search(youtube_regex, url)
    if match:
        return {"type": "youtube", "id": match.group(1)}

    spotify_regex = r"open\.spotify\.com\/(track|album|playlist|episode)\/([a-zA-Z0-9]+)"
    match = re.search(spotify_regex, url)
    if match:
        return {"type": "spotify", "resource": match.group(1), "id": match.group(2)}

    raise HTTPException(status_code=400, detail="URL no válida. Solo YouTube y Spotify")

@app.get("/videos", tags=["Videos"])
def obtener_videos():
    videos = video_engine.listar_videos()
    result = []
    for v in videos:
        data = dict(v.__dict__)
        if v.tipo == "youtube":
            data["embed_url"] = f"https://www.youtube.com/embed/{v.video_id}"
            data["player_url"] = f"https://www.youtube.com/watch?v={v.video_id}"
        elif v.tipo == "spotify":
            data["embed_url"] = f"https://open.spotify.com/embed/track/{v.video_id}"
            data["player_url"] = f"https://open.spotify.com/track/{v.video_id}"
        else:
            data["embed_url"] = None
            data["player_url"] = None
        result.append(data)
    return result

@app.post("/videos/add", tags=["Videos"])
async def registrar_video(url: str):
    url_info = detect_url_type(url)

    async with httpx.AsyncClient() as client:
        if url_info["type"] == "youtube":
            v_id = url_info["id"]
            res = await client.get(f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={v_id}&format=json")
            if res.status_code != 200:
                raise HTTPException(status_code=404, detail="No se pudo obtener info del video")
            data = res.json()
            nuevo_video = Video(
                id=None,
                video_id=v_id,
                titulo=data.get("title", "Sin título"),
                canal_autor=data.get("author_name"),
                tipo="youtube",
                miniatura_url=f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg"
            )
        else:
            res = await client.get(f"https://open.spotify.com/oembed?url={url}")
            if res.status_code != 200:
                raise HTTPException(status_code=404, detail="No se pudo obtener info de la canción")
            data = res.json()
            nuevo_video = Video(
                id=None,
                video_id=url_info["id"],
                titulo=data.get("title", "Sin título"),
                canal_autor=data.get("author_name"),
                tipo="spotify",
                miniatura_url=data.get("thumbnail_url")
            )

    db_id = video_engine.agregar_video(nuevo_video)
    video_data = {**nuevo_video.__dict__, "id": db_id}
    if not video_data.get("fecha_registro"):
        video_data["fecha_registro"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    await ws_manager.broadcast("videos", {
        "type": "video:created",
        "data": video_data
    })
    return {"status": "success", "id": db_id, "video_id": url_info["id"]}

@app.delete("/videos/{id}", tags=["Videos"])
async def borrar_video(id: int):
    if video_engine.eliminar_video(id):
        await ws_manager.broadcast("videos", {
            "type": "video:deleted",
            "data": {"id": id}
        })
        return {"mensaje": "Video eliminado"}
    raise HTTPException(status_code=404, detail="Video no encontrado")

@app.put("/videos/{id}", tags=["Videos"])
async def editar_video(id: int, video: Video):
    if video_engine.editar_video(id, video):
        await ws_manager.broadcast("videos", {
            "type": "video:updated",
            "data": {**video.__dict__, "id": id}
        })
        return {"mensaje": "Video actualizado"}
    raise HTTPException(status_code=404, detail="Video no encontrado")
