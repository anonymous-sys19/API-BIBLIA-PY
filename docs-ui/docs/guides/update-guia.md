# Actualizar Guía de Estudio

Modifica una guía existente por su ID

<div class="endpoint-badge">
  <span class="method put">PUT</span>
  <code class="endpoint-path">/guide/{id}</code>
</div>

```bash
curl -X PUT "https://api.tu-dominio.com/guide/1" \
  -H "Content-Type: application/json" \
  -d '{
    "id": null,
    "title": "La Gracia Salvadora de Dios (Actualizado)",
    "author": "Autor",
    "content": "Contenido actualizado...",
    "tags": "discipulado, fe, gracia",
    "status": "published"
  }'
```

## Respuesta

```json
{
  "mensaje": "Guía actualizada"
}
```

::: info Re-computa HTML
Al editar una guía, el `content_html` se re-genera y actualiza en la base de datos.
:::
