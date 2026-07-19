# Actualizar Radio

Actualiza los datos de una estación existente

<div class="endpoint-badge">
  <span class="method put">PUT</span>
  <code class="endpoint-path">/stream/{radio_id}</code>
</div>

## Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `radio_id` | integer | Sí | ID de la radio (path param) |

## Request Body

Mismos campos que [Agregar Radio](/streaming/add-radio).

## Respuesta

```json
{
  "mensaje": "Radio actualizada"
}
```
