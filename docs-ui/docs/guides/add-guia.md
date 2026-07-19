# Agregar Guía de Estudio

Crea una nueva guía de estudio bíblico

<div class="endpoint-badge">
  <span class="method post">POST</span>
  <code class="endpoint-path">/guide/add</code>
</div>

```bash
curl -X POST "BASE_URL/guide/add" \
  -H "Content-Type: application/json" \
  -d '{
    "id": null,
    "title": "La Gracia Salvadora de Dios",
    "author": "Autor",
    "content": "Tu contenido aquí...",
    "tags": "discipulado, fe",
    "status": "published"
  }'
```

## Parámetros

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | integer/null | Siempre null para crear nuevas guías |
| title | string | Título de la guía |
| author | string | Autor de la guía (opcional) |
| content | string | Contenido completo de la guía (markdown/texto) |
| tags | string | Tags separados por comas. Si se omite, se auto-extraen del contenido |
| status | string | "published" o "draft" (default: "published") |

## Respuesta

```json
{
  "status": "success",
  "id": 1,
  "mensaje": "Guía agregada"
}
```

::: info HTML pre-computado
El `content_html` se genera automáticamente al crear la guía y se cachea en la base de datos para optimizar lecturas futuras.
:::
