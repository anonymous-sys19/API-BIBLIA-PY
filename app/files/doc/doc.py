
def doc_api_json(BIBLIAS: dict) -> dict:
    versiones = {
        "RVR1960": "Reina Valera 1960",
        "NVI": "Nueva Version Internacional",
        "NTV": "Nueva Traduccion Viviente",
        "PDT": "Palabra de Dios para Todos",
        "BAD": "Biblia de las Americas",
        "BLSEE": "Biblia de Lenguaje Sencillo",
        "RVC": "Reina Valera Contemporanea",
        "RVG": "Reina Valera Gomez 2010",
    }

    return {
        "api": "GhostRoot Bible API",
        "version": "1.0.0",
        "endpoints": {
            "/daily": {
                "GET /daily",
                "GET /daily/{version}",
            },
            "/list": {
                "GET /list/testaments",
                "GET /list/books",
                "GET /list/books/antiguo",
                "GET /list/books/nuevo",
            },
            "/info": {
                "GET /info/chapters/{libro_id}",
                "GET /info/verses/{libro_id}/{chapter}",
            },
            "/search": {
                "GET /search/{query}",
            },
            "/capitulo": {
                "GET /{libro}/{capitulo}",
                "GET /bible/{book_id}/{chapter}",
            },
            "/versiculo": {
                "GET /{libro}/{capitulo}/{versiculo}",
                "GET /{libro}/{capitulo}/{versiculo}/{version}",
            },
        },
        "versiones_disponibles": versiones,
        "stream_endpoints": {
            "GET /stream",
            "POST /stream/add",
            "PUT /stream/{radio_id}",
            "DELETE /stream/{radio_id}",
        },
        "video_endpoints": {
            "GET /videos",
            "POST /videos/add?url={url}",
            "POST /videos/import?url={url} — importa canal/playlist (yt-dlp)",
            "POST /videos/import/preview — vista previa de colección",
            "POST /videos/import/selected — importar seleccionados",
            "PUT /videos/{id}",
            "DELETE /videos/{id}",
        },
        "guide_endpoints": {
            "GET /guide — lista guías paginadas (?tag=, ?page=, ?limit=)",
            "GET /guide/tags — lista tags disponibles",
            "GET /guide/{id} — detalle de guía (+ versículos parseados, ?html=true para HTML renderizado)",
            "GET /guide/{id}/verses — textos bíblicos completos de la guía (batch lookup)",
            "POST /guide/add — agregar guía (tags auto-extraídos, HTML pre-computado)",
            "PUT /guide/{id} — editar guía (re-computa HTML cacheado)",
            "DELETE /guide/{id} — eliminar guía",
        },
        "performance": {
            "rate_limit": "120 requests/min por IP",
            "pagination": "Default 20 items, max 100",
            "etag_caching": "ETag + Cache-Control: max-age=60 en endpoints de guías",
            "gzip_compression": "Respuestas > 500 bytes comprimidas automáticamente",
            "precomputed_html": "content_html cacheado en DB al crear/editar guías",
            "batch_verse_lookup": "Deduplica referencias en /guide/{id}/verses",
            "database_indexes": "Índices en status, created_at, guide_tags"
        },
        "websocket_endpoints": {
            "WS /ws/{channel} — canales: videos, streams, biblia",
            "Eventos en tiempo real tras mutaciones CRUD",
        },
        "health": {
            "GET /health",
        },
        "brand_assets": {
            "icon_svg": "/static/img/icon.svg",
            "icon_jpg": "/static/img/icon.jpg",
            "description": "Iconos oficiales de GhostRoot Bible API disponibles para uso público",
            "formats": {
                "svg": {
                    "url": "/static/img/icon.svg",
                    "type": "image/svg+xml",
                    "use_case": "Escalable, ideal para web y apps"
                },
                "jpg": {
                    "url": "/static/img/icon.jpg",
                    "type": "image/jpeg",
                    "use_case": "Compatible universal, ideal para previews y thumbnails"
                }
            }
        },
        "resources": {
            "documentation": "/",
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "admin_panel": "/admin",
            "skill_download": "/download/skill"
        }
    }