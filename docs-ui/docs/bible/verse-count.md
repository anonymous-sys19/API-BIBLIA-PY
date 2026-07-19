# Cantidad de Versículos

Retorna el número total de versículos de un capítulo

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/info/verses/{libro_id}/{chapter}</code>
</div>

## Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `libro_id` | integer | Sí | ID del libro |
| `chapter` | integer | Sí | Número de capítulo |
| `version` | string | No | Versión bíblica (query param) |

## Respuesta

```json
{
  "total": 31
}
```

## Ejemplo

```bash
# Génesis capítulo 1 tiene 31 versículos
curl https://api.tu-dominio.com/info/verses/1/1

# Respuesta: {"total": 31}
```
