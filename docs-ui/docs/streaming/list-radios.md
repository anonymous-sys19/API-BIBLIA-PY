# Lista de Radios

Retorna todas las estaciones de radio registradas

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/stream</code>
</div>

## Respuesta

```json
[
  {
    "id": 5,
    "nombre": "Enlace Juvenil-CR",
    "url_stream": "http://stream.zeno.fm/52hf40q405quv/;",
    "pais": "Costa Rica 88.4FM",
    "genero": "Cristiana",
    "logo_url": "https://cdn.instant.audio/images/logos/radios-co-cr/enlace-juvenil.png",
    "status": "online"
  }
]
```

## Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `id` | integer | ID único de la radio |
| `nombre` | string | Nombre de la estación |
| `url_stream` | string | URL del streaming de audio |
| `pais` | string | País de origen |
| `genero` | string | Género musical/temático |
| `logo_url` | string \| null | URL del logo de la estación |
| `status` | string | Estado: "online" u "offline" |
