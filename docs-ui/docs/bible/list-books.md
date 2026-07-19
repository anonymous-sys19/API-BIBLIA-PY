# Lista de Libros

Retorna todos los libros bíblicos con filtrado por testamento

<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/list/books</code>
</div>
<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/list/books?testament={id}</code>
</div>
<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/list/books/antiguo</code>
</div>
<div class="endpoint-badge">
  <span class="method get">GET</span>
  <code class="endpoint-path">/list/books/nuevo</code>
</div>

## Parámetros

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `version` | string | No | Versión bíblica (query param) |
| `testament` | integer | No | ID del testamento: 1 (Antiguo), 2 (Nuevo), 3 (Apócrifos) |

## Respuesta

```json
[
  {
    "id": 1,
    "name": "Génesis",
    "abbreviation": "Gen",
    "testament_id": 1,
    "testament": "Old Testament"
  },
  {
    "id": 2,
    "name": "Éxodo",
    "abbreviation": "Exo",
    "testament_id": 1,
    "testament": "Old Testament"
  }
]
```

## Ejemplo de Consumo

```javascript
function BooksList() {
  const [books, setBooks] = useState([]);
  const [testament, setTestament] = useState(null);

  useEffect(() => {
    const url = testament
      ? `/list/books?testament=${testament}`
      : '/list/books';

    fetch(url)
      .then(res => res.json())
      .then(data => setBooks(data));
  }, [testament]);

  return (
    <div>
      <select onChange={e => setTestament(e.target.value)}>
        <option value="">Todos</option>
        <option value="1">Antiguo Testamento</option>
        <option value="2">Nuevo Testamento</option>
      </select>

      <ul>
        {books.map(book => (
          <li key={book.id}>
            {book.name} ({book.abbreviation})
          </li>
        ))}
      </ul>
    </div>
  );
}
```
