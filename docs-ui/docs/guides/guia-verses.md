# Obtener Versículos de una Guía

Textos bíblicos completos de todas las referencias en la guía (batch lookup con deduplicación)

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/guide/{id}/verses</code>
</div>

```bash
curl -X GET "https://api.tu-dominio.com/guide/1/verses"
```

## Con versión específica

```bash
curl -X GET "https://api.tu-dominio.com/guide/1/verses?version=nvi"
```

## Respuesta

```json
[
  {
    "id": 26137,
    "book_id": 43,
    "book_name": "Juan",
    "chapter": 3,
    "verse": 16,
    "text": "Porque de tal manera amó Dios al mundo...",
    "version": "rvr1960"
  },
  {
    "id": 27845,
    "book_id": 45,
    "book_name": "Romanos",
    "chapter": 8,
    "verse": 28,
    "text": "Y sabemos que a los que aman a Dios...",
    "version": "rvr1960"
  }
]
```

::: info Batch lookup
Las referencias se deduplican automáticamente. Si la guía menciona "Juan 3:16" tres veces, solo se consulta una vez.
:::
