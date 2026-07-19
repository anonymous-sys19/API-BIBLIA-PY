# Códigos de Error

Respuestas de error estandarizadas

## Códigos HTTP

| Código | Significado | Descripción |
|--------|-------------|-------------|
| `200` | OK | La solicitud se completó correctamente |
| `400` | Bad Request | La solicitud es inválida o falta un parámetro requerido |
| `404` | Not Found | El recurso solicitado no existe |
| `500` | Internal Error | Error interno del servidor |

## Formato de Error

```json
{
  "detail": "Libro 'invalido' no encontrado"
}
```
