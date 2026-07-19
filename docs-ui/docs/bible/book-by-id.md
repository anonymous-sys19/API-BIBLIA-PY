# Libro por ID

Obtén un libro específico por su ID numérico

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/books/{book_id}</code>
</div>

## Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `book_id` | integer | Sí | ID del libro |
| `version` | string | No | Versión bíblica (query param) |

## Respuesta

```json
{
  "id": 1,
  "name": "Génesis",
  "abbreviation": "Gen",
  "testament_id": 1,
  "testament": "Old Testament"
}
```

::: info
Los IDs de los libros se pueden obtener del endpoint `/list/books`. El testamento se corrige dinámicamente según el canon estándar.
:::

## Ejemplo de Consumo

```javascript
async function getBook(bookId, version = 'rvr1960') {
  const response = await fetch(`/books/${bookId}?version=${version}`);
  if (!response.ok) throw new Error('Libro no encontrado');
  return response.json();
}

// Uso
const book = await getBook(1);
console.log(book.name); // "Génesis"
```
