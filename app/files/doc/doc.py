
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
            "PUT /videos/{id}",
            "DELETE /videos/{id}",
        },
        "health": {
            "GET /health",
        },
    }