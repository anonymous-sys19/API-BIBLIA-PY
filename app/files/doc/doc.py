
def doc_api_json( BIBLIAS):
    return {
        "api": "GhostRoot Bible API",
        "version": "1.0.0",
        "endpoints": {
            "/daily": {
                "GET: /daily/{version}",
                "GET: /daily"
            },
            "/list/books": {
                "GET: /list/books/{version}",
                "GET: /list/books",
            },
            "/search": {
                "GET: /search/{query}/{version}",
                "GET: /search/{query}"
            },
            "/libro/capitulo/versiculo": {
                "GET: /{libro}/{capitulo}/{versiculo}/{version}",
                "GET: /{libro}/{capitulo}/{versiculo}"
            },
            
        },
        
       
        "versiones_disponibles":{
            list(BIBLIAS.keys())[0].upper(): "Reina Valera 1960",
            list(BIBLIAS.keys())[1].upper(): "Nueva Version Internacional",
            list(BIBLIAS.keys())[2].upper(): "Nueva Traduccion Viviente",
            list(BIBLIAS.keys())[3].upper(): "Palabra de Dios para Todos",
            list(BIBLIAS.keys())[4].upper(): "Biblia de las Americas",
            list(BIBLIAS.keys())[5].upper(): "Biblia de Lenguaje Sencillo",
            list(BIBLIAS.keys())[6].upper(): "Reina Valera Contemporanea",
            list(BIBLIAS.keys())[7].upper(): "Reina Valera Gomez 2010",
            # "LBLA": "La Biblia de Las Americas" Proximamente
        },
        
        "stream_endpoints": {
            "GET: /stream",
            "POST: /stream/add",
            "GET: /stream/{radio_id}",
            "PUT: /stream/{radio_id}/edit",
            "DELETE: /stream/{radio_id}/delete",
        },
        "video_endpoints": {
            "GET: /videos",
            "POST: /videos/add",
            "PUT: /videos/{video_id}",
            "DELETE: /videos/{video_id}/delete"
        }

    } 