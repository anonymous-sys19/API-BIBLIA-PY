
from fastapi import FastAPI, HTTPException
from typing import Optional
from app.db.database import BibliaEngine, StreamManager, VideoManager
from fastapi import FastAPI, HTTPException
from app.db.models import RadioStream, Video, normalizar, BIBLIAS_VERSIONES
import re
import httpx

from app.files.doc.doc import doc_api_json
# nos aseguramos el cors para que cualquier frontend pueda consumir la API sin problemas
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="API BIBLICA - GHOSTROOT DEV")
BIBLIAS = BIBLIAS_VERSIONES() #agregamos todas las versiones de la biblia  a modelos
engine = BibliaEngine(BIBLIAS) # Inicializamos el motor con las versiones de la biblia


stream_engine = StreamManager("app/files/radio.sqlite")
video_engine = VideoManager("app/files/radio.sqlite")  # Usamos el mismo SQLite para simplicidad


# Configuración CORS para permitir acceso desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las URLs
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todas las cabeceras
    allow_credentials=True
)

@app.get("/")
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


# --- RUTAS DE RADIO STREAMING ---


@app.get("/stream", tags=["Streaming"])
def listar_radios():
    """Endpoint para que tu web muestre todas las radios[cite: 2]."""
    return stream_engine.listar_radios()

@app.post("/stream/add", tags=["Streaming"])
def nueva_radio(radio: RadioStream):
    """
    Agrega una radio. 
    Ejemplo de JSON: {"nombre": "Radio Vida", "url_stream": "https://..."}[cite: 1, 2]
    """
    radio_id = stream_engine.agregar_radio(radio)
    if radio_id:
        return {"status": "success", "id": radio_id, "mensaje": "Radio agregada"}
    raise HTTPException(status_code=400, detail="Error al agregar radio")

@app.delete("/stream/{radio_id}", tags=["Streaming"])
def borrar_radio(radio_id: int):
    """Elimina una radio si ya no funciona[cite: 2]."""
    if stream_engine.eliminar_radio(radio_id):
        return {"mensaje": "Radio eliminada"}
    raise HTTPException(status_code=404, detail="No se encontró la radio")

@app.put("/stream/{radio_id}", tags=["Streaming"])
def editar_radio(radio_id: int, radio: RadioStream):
    """Actualiza datos de una radio[cite: 1]."""
    if stream_engine.editar_radio(radio_id, radio):
        return {"mensaje": "Radio actualizada"}
    raise HTTPException(status_code=404, detail="No se encontró la radio")

# --- RUTAS DE VIDEO STREAMING (FUTURAS EXPANSIONES) ---


# Inicializamos el gestor (puedes usar el mismo sqlite de radio)

# --- LÓGICA DE VIDEOS ---

def extraer_youtube_id(url: str) -> str:
    """Extrae el ID de 11 caracteres de una URL de YouTube."""
    regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(regex, url)
    if not match:
        raise HTTPException(status_code=400, detail="URL de YouTube inválida")
    return match.group(1)

@app.get("/videos", tags=["Videos"])
def obtener_videos():
    return video_engine.listar_videos()

@app.post("/videos/add", tags=["Videos"])
async def registrar_video(url: str):
    """
    Recibe la URL, extrae el ID y busca automáticamente el título y miniatura.
    """
    v_id = extraer_youtube_id(url)
    
    # Consultamos datos básicos a YouTube (oEmbed) sin necesidad de API KEY
    async with httpx.AsyncClient() as client:
        res = await client.get(f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={v_id}&format=json")
        if res.status_code != 200:
            raise HTTPException(status_code=404, detail="No se pudo obtener info del video")
        
        data = res.json()
        nuevo_video = Video(
            id=None,
            video_id=v_id,
            titulo=data.get("title", "Sin título"),
            canal_autor=data.get("author_name"),
            tipo="video",
            miniatura_url=f"https://i.ytimg.com/vi/{v_id}/hqdefault.jpg"
        )
        
    db_id = video_engine.agregar_video(nuevo_video)
    return {"status": "success", "id": db_id, "video_id": v_id}

@app.delete("/videos/{id}", tags=["Videos"])
def borrar_video(id: int):
    if video_engine.eliminar_video(id):
        return {"mensaje": "Video eliminado"}
    raise HTTPException(status_code=404, detail="Video no encontrado")
@app.put("/videos/{id}", tags=["Videos"])
def editar_video(id: int, video: Video):
    """Actualiza metadatos de un video (título, autor, miniatura)."""
    if video_engine.editar_video(id, video):
        return {"mensaje": "Video actualizado"}
    raise HTTPException(status_code=404, detail="Video no encontrado")
