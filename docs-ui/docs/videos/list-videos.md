# Lista de Videos

Retorna todos los videos registrados

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/videos</code>
</div>

## Respuesta

```json
[
  {
    "id": 37,
    "video_id": "PjYcsu7EnJE",
    "titulo": "Rio de Vida",
    "canal_autor": "ELOI",
    "tipo": "video",
    "miniatura_url": "https://i.ytimg.com/vi/PjYcsu7EnJE/hqdefault.jpg",
    "fecha_registro": "2026-06-07 20:22:35"
  }
]
```

## Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID único en base de datos |
| `video_id` | string | ID de YouTube (11 caracteres) |
| `titulo` | string | Título del video |
| `canal_autor` | string \| null | Nombre del canal |
| `tipo` | string | Tipo de contenido (siempre "video") |
| `miniatura_url` | string \| null | URL de la miniatura |
| `fecha_registro` | string \| null | Fecha de registro (YYYY-MM-DD HH:MM:SS) |
