# Actualizar Video

Actualiza metadatos de un video

<div class="endpoint-badge">
  <span class="method put">PUT</span>
  <code class="endpoint-path">/videos/{id}</code>
</div>

## Request Body

```json
{
  "id": 37,
  "video_id": "PjYcsu7EnJE",
  "titulo": "Nuevo Título",
  "canal_autor": "Nuevo Canal",
  "tipo": "video",
  "miniatura_url": "https://nueva-url.com/thumb.jpg"
}
```

## Respuesta

```json
{
  "mensaje": "Video actualizado"
}
```
