# Agregar Video

Registra un video desde URL de YouTube (extrae datos automáticamente)

<div class="endpoint-badge">
  <span class="method post">POST</span>
  <code class="endpoint-path">/videos/add?url={youtube_url}</code>
</div>

## Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `url` | string | Sí | URL completa de YouTube |

## Respuesta

```json
{
  "status": "success",
  "id": 38,
  "video_id": "PjYcsu7EnJE"
}
```

## Ejemplo

```javascript
const addYouTubeVideo = async (youtubeUrl) => {
  const response = await fetch(
    `https://api.tu-dominio.com/videos/add?url=${encodeURIComponent(youtubeUrl)}`,
    { method: 'POST' }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Error al agregar video');
  }

  return await response.json();
};

// Uso
const result = await addYouTubeVideo('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
console.log(`Video registrado con ID: ${result.id}`);
```
