# Lista de Videos

Retorna todos los videos registrados

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/videos</code>
</div>

## Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `page` | integer | No | Número de página (activa respuesta paginada) |
| `limit` | integer | No | Items por página (default: 20, max: 100) |

## Respuesta (completa)

```json
[
  {
    "id": 37,
    "video_id": "PjYcsu7EnJE",
    "titulo": "Rio de Vida",
    "canal_autor": "ELOI",
    "tipo": "video",
    "miniatura_url": "https://i.ytimg.com/vi/PjYcsu7EnJE/hqdefault.jpg",
    "fecha_registro": "2026-06-07 20:22:35",
    "embed_url": "https://www.youtube.com/embed/PjYcsu7EnJE",
    "player_url": "https://www.youtube.com/watch?v=PjYcsu7EnJE"
  }
]
```

## Respuesta (paginada)

```json
{
  "data": [
    {
      "id": 37,
      "video_id": "PjYcsu7EnJE",
      "titulo": "Rio de Vida",
      "canal_autor": "ELOI",
      "tipo": "video",
      "miniatura_url": "https://i.ytimg.com/vi/PjYcsu7EnJE/hqdefault.jpg",
      "fecha_registro": "2026-06-07 20:22:35",
      "embed_url": "https://www.youtube.com/embed/PjYcsu7EnJE",
      "player_url": "https://www.youtube.com/watch?v=PjYcsu7EnJE"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 50,
    "pages": 3
  }
}
```

## Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID único en base de datos |
| `video_id` | string | ID de YouTube (11 caracteres) o Spotify |
| `titulo` | string | Título del video |
| `canal_autor` | string \| null | Nombre del canal/artista |
| `tipo` | string | `"youtube"` \| `"spotify"` |
| `miniatura_url` | string \| null | URL de la miniatura |
| `embed_url` | string | URL para iframe embedding |
| `player_url` | string | URL directa en la plataforma |
| `fecha_registro` | string \| null | Fecha de registro (YYYY-MM-DD HH:MM:SS) |
