# Obtener Capítulo

Retorna todos los versículos de un capítulo

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/{libro}/{capitulo}</code>
</div>
<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/bible/{book_id}/{chapter}</code>
</div>

## Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `libro` | string | Sí | Nombre o abreviatura del libro (insensible a tildes/mayúsculas) |
| `book_id` | integer | Sí | ID del libro (alternativa a nombre) |
| `capitulo` | integer | Sí | Número de capítulo |
| `version` | string | No | Versión bíblica (query param) |

## Respuesta

```json
[
  {
    "id": 1,
    "book_id": 1,
    "book_name": "Génesis",
    "chapter": 1,
    "verse": 1,
    "text": "En el principio creó Dios los cielos y la tierra.",
    "version": "rvr1960"
  },
  {
    "id": 2,
    "book_id": 1,
    "book_name": "Génesis",
    "chapter": 1,
    "verse": 2,
    "text": "Y la tierra estaba desordenada y vacía, y las tinieblas estaban sobre la faz del abismo, y el Espíritu de Dios se movía sobre la faz de las aguas.",
    "version": "rvr1960"
  }
]
```

## Ejemplos de Consumo

```javascript
// Por nombre
const getChapter = async (libro, capitulo, version = 'rvr1960') => {
  const response = await fetch(
    `BASE_URL/${libro}/${capitulo}?version=${version}`
  );
  return await response.json();
};

// Por ID
const getChapterById = async (bookId, chapter, version = 'rvr1960') => {
  const response = await fetch(
    `BASE_URL/bible/${bookId}/${chapter}?version=${version}`
  );
  return await response.json();
};

// Uso
const genesis1 = await getChapter('genesis', 1);
const juan3 = await getChapter('juan', 3, 'nvi');
```
