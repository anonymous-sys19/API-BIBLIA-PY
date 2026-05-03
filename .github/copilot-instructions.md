# AI Coding Agent Instructions - API-BIBLIA-PY

## Project Overview

**API-BIBLIA-PY** is a production-ready Bible data API built with Python, serving biblical content through SQLite. The project uses FastAPI for HTTP routing and provides verse data in Spanish (RVR1960 translation) with scalable, RESTful endpoints.

## Architecture

### Core Components

#### Database Layer (`app/db/database.py`)

- **Class**: `Biblia` - Main data access layer
- **Primary Database**: SQLite (`rvr1960.sqlite`)
- **Connection Pattern**: Context managers (`@contextmanager`) for automatic connection cleanup
- **Data Classes**:
  - `Verso`: Individual verse with book, chapter, verse, text metadata
  - `Libro`: Book with testament relationship and chapter count

**Schema Structure**:

- `book` (id, testament_id, name, abbreviation)
- `testament` (id, name) - 1=OT, 2=NT
- `verse` (id, book_id, chapter, verse, text) - Primary queries indexed by (book_id, chapter, verse)
- `metadata` (key, value) - Version tracking and configuration

**Critical Pattern**: All queries must join through `book` and `testament` tables. Use `testament_id` for filtering OT/NT data.

#### API Layer (`app/main.py`)

- **Framework**: FastAPI with automatic OpenAPI docs at `/docs`
- **CORS**: Enabled for all origins (configurable via middleware)
- **Error Handling**: HTTPException with status codes and descriptive messages
- **Response Format**: Consistent JSON structure with referencia, testamento, and total counts

**Endpoints Architecture**:

1. `/libros` - List books with optional testament filter
2. `/libros/{abreviatura}` - Single book lookup (Ej: "Mat", "Jn")
3. `/verso/{libro}/{capitulo}/{versiculo}` - Single verse (Ej: `/verso/Jn/3/16`)
4. `/capitulo/{libro}/{capitulo}` - All verses in chapter
5. `/rango/{libro}/{cap_inicio}/{ver_inicio}/{cap_fin}/{ver_fin}` - Verse range
6. `/buscar?q=término&testamento=1&limit=100` - Full-text search with pagination
7. `/health` - Database connection and statistics

### Configuration (`app/files/db-info.md`)

- Documents database schema visually with table definitions
- Update when schema changes; reference for debugging queries

### Environment Configuration (`.env`)

```
DB_PATH=rvr1960.sqlite                           # Database file location
STREAM_URL_PROD=https://centova.hostingtico.com:7016/  # Production streaming
STREAM_URL_DEV=https://localhost:3000/stream/           # Development streaming
STREAM_URL=${STREAM_URL_DEV}                     # Active endpoint
API_HOST=0.0.0.0                                 # Bind address
API_PORT=8000                                    # Server port
API_DEBUG=false                                  # Debug mode toggle
```

## Key Patterns & Conventions

### Database Access Pattern

```python
def obtener_verso(self, book_id: int, chapter: int, verse: int) -> Optional[Verso]:
    with self._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT v.id, v.book_id, b.name, b.abbreviation, v.chapter, v.verse, v.text, t.name
            FROM verse v
            JOIN book b ON v.book_id = b.id
            JOIN testament t ON b.testament_id = t.id
            WHERE v.book_id = ? AND v.chapter = ? AND v.verse = ?
        """, (book_id, chapter, verse))
        # Always use ? placeholders for SQL injection prevention
```

**Rules**:

1. Always filter by `testament_id` when relevant (data isolation)
2. Use parameterized queries (?) - never string concatenation
3. Join through `book` and `testament` for complete metadata
4. Return dataclass objects (`Verso`, `Libro`) for type safety
5. Use `LIMIT` clause for search queries to prevent excessive DB load

### API Response Format

Every endpoint returns consistent JSON:

```json
{
  "referencia": "Juan 3:16",
  "total_versos": 1,
  "versos": [...],
  "testamento": "Nuevo"
}
```

### Error Handling

- SQLite errors → `HTTPException(status_code=500, detail=error_message)`
- Missing resources → `HTTPException(status_code=404, detail="...")`
- Invalid queries → `HTTPException(status_code=400, detail="...")`
- Always catch and log exceptions in DB layer

### Naming Conventions

- Spanish terminology: `testamento`, `versículo`, `libro`, `capítulo`
- Abbreviations follow biblical standard: `Mat`, `Jn`, `Rom`, `Tit`
- Maintain Spanish in API responses and documentation

## Development Workflow

### Setup

```bash
cd /home/ghostroot/Documentos/GIT/API-BIBLIA-PY
source venv/bin/activate
pip install -r requirements.txt
```

### Running the API

```bash
# Development mode (auto-reload enabled)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Project Structure

```
app/
  main.py              # FastAPI endpoints (7 route groups)
  db/
    database.py        # Biblia class with 10+ query methods
  files/
    db-info.md         # Database schema documentation
```

## Integration Points

- **HTTP API**: FastAPI auto-generates OpenAPI docs at `/docs`
- **Bible Database**: SQLite read-only access via `Biblia` class
- **Streaming Service**: `STREAM_URL` environment variable (not yet integrated)
- **Monitoring**: `/health` endpoint for uptime checks

## Common Tasks

### Adding New Endpoints

1. Create query method in `Biblia` class (e.g., `obtener_versos_por_palabra()`)
2. Add route in `app/main.py` with `@app.get()` decorator
3. Return consistent JSON structure with referencia field
4. Use `HTTPException` for errors with appropriate status codes
5. Test with `/docs` UI

### Querying Verses - Query by Reference

```python
# Get single verse
verso = biblia.obtener_verso(book_id=40, chapter=3, verse=16)  # John 3:16

# Get chapter
versos = biblia.obtener_capitulo(book_id=40, chapter=3)

# Get range
versos = biblia.obtener_rango_versos(book_id=40, 3, 16, 3, 18)

# Search
resultados = biblia.buscar_en_versos("amor", testament_id=2, limit=50)
```

### Adding Database Indices

When adding features that query frequently:

1. Create migration file documenting the index
2. Update `app/files/db-info.md` with new indices
3. Test performance before/after

## Scalability Considerations

### Current Limitations & Future Enhancements

1. **Caching Layer**: Add Redis for frequent queries (`/libros`, popular verses)
   - Cache key pattern: `biblia:verso:{book_id}:{chapter}:{verse}`
2. **Search Optimization**: SQLite FTS (Full-Text Search) table for `buscar` endpoint
3. **Connection Pooling**: Replace direct SQLite for high-concurrency (consider PostgreSQL)
4. **Pagination**: Implement offset/limit for large result sets in search
5. **Rate Limiting**: Add middleware to prevent abuse on search endpoint

### Current Performance Baseline

- Database: ~31,000 verses in SQLite
- Single verse lookup: < 5ms (indexed by primary key)
- Chapter lookup: ~50-100ms depending on verse count
- Full-text search: ~200-500ms for common terms

## Notes for AI Agents

- FastAPI automatically validates query parameters and generates OpenAPI docs
- Always use stemmed query pattern with book abbreviation lookup for verse references (users may pass "Matthew" or "Mat")
- Bible data is read-only in production (no INSERT/UPDATE/DELETE on verses)
- Maintain Spanish language context in database references and responses
- The `/health` endpoint returns statistics useful for monitoring integration
- Verse references follow format: `{abbreviation} {chapter}:{verse}` (Ej: "Jn 3:16")
