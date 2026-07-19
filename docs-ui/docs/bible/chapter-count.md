# Cantidad de Capítulos

Retorna el número total de capítulos de un libro

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/info/chapters/{libro_id}</code>
</div>

## Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `libro_id` | integer | Sí | ID del libro (path param) |
| `version` | string | No | Versión bíblica (query param) |

## Respuesta

```json
{
  "total": 50
}
```

## Ejemplo

```bash
# Génesis tiene 50 capítulos
curl https://api.tu-dominio.com/info/chapters/1

# Respuesta: {"total": 50}
```
