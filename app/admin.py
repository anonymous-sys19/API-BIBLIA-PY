from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import os
import httpx
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader

from app.db.database import StreamManager, VideoManager
from app.db.models import RadioStream, Video

load_dotenv()

jinja_env = Environment(loader=FileSystemLoader("app/templates"))

def render_template(template_name: str, context: dict, request: Request):
    # Garantiza que flash y flash_type siempre existan para evitar UndefinedError
    context.setdefault("flash", None)
    context.setdefault("flash_type", "success")
    template = jinja_env.get_template(template_name)
    return HTMLResponse(template.render(request=request, **context))

TURSO_DB_URL = os.getenv("TURSO_DB_URL", "")
TURSO_AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

stream_manager = StreamManager(TURSO_DB_URL, TURSO_AUTH_TOKEN)
video_manager = VideoManager(TURSO_DB_URL, TURSO_AUTH_TOKEN)


def admin_routes(app: FastAPI):
    
    @app.get("/admin", response_class=HTMLResponse)
    async def admin_home(request: Request):
        return RedirectResponse(url="/admin/streams", status_code=302)

    @app.get("/admin/streams", response_class=HTMLResponse)
    async def admin_streams(request: Request):
        streams = stream_manager.listar_radios()
        streams_dict = [{"id": s.id, "nombre": s.nombre, "url_stream": s.url_stream, "pais": s.pais, "genero": s.genero, "logo_url": s.logo_url, "status": s.status} for s in streams]
        flash = request.query_params.get("msg")
        flash_type = request.query_params.get("type", "success")
        return render_template("admin/streams.html", {"active": "streams", "streams": streams_dict, "flash": flash, "flash_type": flash_type}, request)

    @app.get("/admin/streams/new", response_class=HTMLResponse)
    async def new_stream(request: Request):
        return render_template("admin/stream_form.html", {"active": "streams", "stream": None}, request)

    @app.post("/admin/streams/new")
    async def create_stream(
        nombre: str = Form(...),
        url_stream: str = Form(...),
        pais: str = Form("Costa Rica"),
        genero: str = Form("Cristiana"),
        logo_url: str = Form(""),
        status: str = Form("online")
    ):
        radio = RadioStream(id=None, nombre=nombre, url_stream=url_stream, pais=pais, genero=genero, logo_url=logo_url or None, status=status)
        stream_manager.agregar_radio(radio)
        return RedirectResponse(url="/admin/streams?msg=Radio+creada+exitosamente&type=success", status_code=303)

    @app.get("/admin/streams/edit/{stream_id}", response_class=HTMLResponse)
    async def edit_stream(request: Request, stream_id: int):
        streams = stream_manager.listar_radios()
        stream = next((s for s in streams if s.id == stream_id), None)
        if not stream:
            raise HTTPException(status_code=404, detail="Radio no encontrada")
        stream_dict = {"id": stream.id, "nombre": stream.nombre, "url_stream": stream.url_stream, "pais": stream.pais, "genero": stream.genero, "logo_url": stream.logo_url, "status": stream.status}
        return render_template("admin/stream_form.html", {"active": "streams", "stream": stream_dict}, request)

    @app.post("/admin/streams/edit/{stream_id}")
    async def update_stream(
        stream_id: int,
        nombre: str = Form(...),
        url_stream: str = Form(...),
        pais: str = Form("Costa Rica"),
        genero: str = Form("Cristiana"),
        logo_url: str = Form(""),
        status: str = Form("online")
    ):
        radio = RadioStream(id=None, nombre=nombre, url_stream=url_stream, pais=pais, genero=genero, logo_url=logo_url or None, status=status)
        stream_manager.editar_radio(stream_id, radio)
        return RedirectResponse(url="/admin/streams?msg=Radio+actualizada+exitosamente&type=success", status_code=303)

    @app.post("/admin/streams/delete/{stream_id}")
    async def delete_stream(stream_id: int):
        stream_manager.eliminar_radio(stream_id)
        return RedirectResponse(url="/admin/streams?msg=Radio+eliminada&type=success", status_code=303)

    @app.get("/admin/videos", response_class=HTMLResponse)
    async def admin_videos(request: Request):
        videos = video_manager.listar_videos()
        videos_dict = [{"id": v.id, "video_id": v.video_id, "titulo": v.titulo, "canal_autor": v.canal_autor, "tipo": v.tipo, "miniatura_url": v.miniatura_url, "fecha_registro": str(v.fecha_registro) if v.fecha_registro else None} for v in videos]
        flash = request.query_params.get("msg")
        flash_type = request.query_params.get("type", "success")
        return render_template("admin/videos.html", {"active": "videos", "videos": videos_dict, "flash": flash, "flash_type": flash_type}, request)

    @app.get("/admin/videos/new", response_class=HTMLResponse)
    async def new_video(request: Request):
        return render_template("admin/video_form.html", {"active": "videos", "video": None}, request)

    @app.post("/admin/videos/new")
    async def create_video(request: Request, url: str = Form(...)):
        """
        Delega la creación al endpoint original /videos/add de la API.
        No duplica lógica: toda la extracción y fetch de YouTube la maneja main.py.
        """
        try:
            # Llamada interna al endpoint real de la API
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(
                    f"http://127.0.0.1:8000/videos/add",
                    params={"url": url}   # /videos/add recibe url como query param
                )
            if res.status_code == 200:
                return RedirectResponse(
                    url="/admin/videos?msg=Video+agregado+exitosamente&type=success",
                    status_code=303
                )
            # El endpoint original devuelve el detalle del error
            detail = res.json().get("detail", "Error al agregar el video")
            return RedirectResponse(
                url=f"/admin/videos/new?msg={detail}&type=error",
                status_code=303
            )
        except Exception as e:
            return RedirectResponse(
                url=f"/admin/videos/new?msg=Error+de+conexión+interna&type=error",
                status_code=303
            )

    @app.get("/admin/videos/edit/{video_id}", response_class=HTMLResponse)
    async def edit_video(request: Request, video_id: int):
        videos = video_manager.listar_videos()
        video = next((v for v in videos if v.id == video_id), None)
        if not video:
            raise HTTPException(status_code=404, detail="Video no encontrado")
        video_dict = {"id": video.id, "video_id": video.video_id, "titulo": video.titulo, "canal_autor": video.canal_autor, "tipo": video.tipo, "miniatura_url": video.miniatura_url}
        return render_template("admin/video_form.html", {"active": "videos", "video": video_dict}, request)

    @app.post("/admin/videos/edit/{video_id}")
    async def update_video(
        video_id: int,
        video_id_orig: str = Form(...),
        titulo: str = Form(...),
        canal_autor: str = Form(""),
        miniatura_url: str = Form(""),
        tipo: str = Form("video")
    ):
        video = Video(id=None, video_id=video_id_orig, titulo=titulo, canal_autor=canal_autor or None, tipo=tipo, miniatura_url=miniatura_url or None)
        video_manager.editar_video(video_id, video)
        return RedirectResponse(url="/admin/videos?msg=Video+actualizado+exitosamente&type=success", status_code=303)

    @app.post("/admin/videos/delete/{video_id}")
    async def delete_video(video_id: int):
        video_manager.eliminar_video(video_id)
        return RedirectResponse(url="/admin/videos?msg=Video+eliminado&type=success", status_code=303)