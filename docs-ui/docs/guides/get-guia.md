# Obtener Guía de Estudio

Recupera una guía individual por su ID

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/guide/{id}</code>
</div>

```bash
curl -X GET "https://api.tu-dominio.com/guide/1"
```

## Con HTML enriquecido

Agrega `?html=true` para obtener el contenido con referencias bíblicas convertidas a enlaces interactivos.

```bash
curl -X GET "https://api.tu-dominio.com/guide/1?html=true"
```

## Respuesta

```json
{
  "id": 1,
  "title": "La Gracia Salvadora de Dios",
  "author": "Autor",
  "content": "...",
  "content_html": "<p>... <a href=\"/efesios/2/8\" class=\"bible-ref\">Efesios 2:8-9</a> ...</p>",
  "tags": "discipulado, fe, gracia",
  "tag_list": ["discipulado", "fe", "gracia"],
  "status": "published",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z",
  "versiculos": [
    {
      "book_id": 49,
      "book_name": "Efesios",
      "chapter": 2,
      "verse_start": 8,
      "verse_end": 9,
      "reference": "Efesios 2:8-9"
    }
  ]
}
```

::: info Enlaces de versículos
Las referencias bíblicas en `content_html` apuntan directamente al versículo (ej: `/efesios/2/8`), no al capítulo completo. Los nombres de libros usan espacios (ej: `/2 corintios/3/18`).
:::

::: info HTML pre-computado
El `content_html` se genera y cachea en la base de datos al crear/editar la guía, no en cada request.
:::
