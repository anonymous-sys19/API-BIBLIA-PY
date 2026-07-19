# Obtener Versículo

Retorna un versículo específico

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/{libro}/{capitulo}/{versiculo}</code>
</div>
<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/{libro}/{capitulo}/{versiculo}/{version}</code>
</div>

## Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `libro` | string | Sí | Nombre o abreviatura del libro |
| `capitulo` | integer | Sí | Número de capítulo |
| `versiculo` | integer | Sí | Número de versículo |
| `version` | string | No | Versión bíblica (path o query param) |

## Respuesta

```json
{
  "id": 26137,
  "book_id": 43,
  "book_name": "Juan",
  "chapter": 3,
  "verse": 16,
  "text": "Porque de tal manera amó Dios al mundo, que ha dado a su Hijo unigénito, para que todo aquel que en él cree, no se pierda, mas tenga vida eterna.",
  "version": "rvr1960"
}
```

## Ejemplos

```bash
# Juan 3:16
curl BASE_URL/juan/3/16

# Con versión en path
curl BASE_URL/juan/3/16/nvi

# Con versión en query
curl "BASE_URL/juan/3/16?version=nvi"
```
