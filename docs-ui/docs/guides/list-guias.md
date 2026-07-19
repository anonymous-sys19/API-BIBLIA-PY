# Lista de Guías de Estudio

Obtén guías de estudio bíblico paginadas con filtros opcionales

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/guide</code>
</div>

```bash
curl -X GET "BASE_URL/guide"
```

## Parámetros de Paginación

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| page | integer | Número de página (default: 1) |
| limit | integer | Items por página (default: 20, max: 100) |
| tag | string | Filtrar por tag específico |

## Filtrar por Tag

```bash
curl -X GET "BASE_URL/guide?tag=discipulado&page=1&limit=10"
```

## Respuesta Paginada

```json
{
  "data": [
    {
      "id": 1,
      "title": "La Gracia Salvadora de Dios",
      "author": "Autor",
      "tags": "discipulado, fe, gracia",
      "tag_list": ["discipulado", "fe", "gracia"],
      "status": "published",
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1
  }
}
```

::: info Caché ETag
Las respuestas incluyen headers `ETag` y `Cache-Control: max-age=60` para optimizar peticiones repetidas.
:::

## Listar todas las etiquetas

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/guide/tags</code>
</div>

```bash
curl -X GET "BASE_URL/guide/tags"
```

```json
["discipulado", "fe", "gracia", "oracion"]
```
