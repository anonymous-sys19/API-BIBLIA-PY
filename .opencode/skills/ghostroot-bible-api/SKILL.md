# GhostRoot Bible API Skill

## Overview

GhostRoot Bible API is a RESTful service for accessing Bible scriptures in multiple Spanish translations, managing Christian radio streams, and YouTube video content.

## Base URL

**Production:** `https://api-biblia-py.onrender.com`
**Local Development:** `http://localhost:8000`

The API automatically detects the environment. Use the appropriate base URL for your context.

## Authentication

- **GET endpoints**: Public, no authentication required
- **POST/PUT/DELETE endpoints**: Currently open for development

## Available Bible Versions

| Code | Name |
|------|------|
| `rvr1960` | Reina Valera 1960 (default) |
| `nvi` | Nueva Version Internacional |
| `ntv` | Nueva Traduccion Viviente |
| `pdt` | Palabra de Dios para Todos |
| `bad` | Biblia de las Americas |
| `blsee` | Biblia de Lenguaje Sencillo |
| `rvc` | Reina Valera Contemporanea |
| `rvg` | Reina Valera Gomez 2010 |

## Endpoints

### Bible Endpoints

#### GET /health
Returns API health status.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

#### GET /daily
Returns a random daily verse that changes each day.

**Parameters:**
- `version` (query, optional): Bible version code (default: rvr1960)

**Response:**
```json
{
  "id": 27845,
  "book_id": 44,
  "book_name": "Hechos",
  "chapter": 26,
  "verse": 21,
  "text": "Por causa de esto los judios, prendiendome en el templo, intentaron matarme.",
  "version": "rvr1960"
}
```

#### GET /daily/{version}
Returns daily verse in specified version.

#### GET /list/testaments
Returns all available testaments.

**Response:**
```json
[
  { "id": 1, "name": "Old Testament" },
  { "id": 2, "name": "New Testament" },
  { "id": 3, "name": "Apocrypha" }
]
```

#### GET /list/books
Returns all Bible books.

**Parameters:**
- `version` (query, optional): Bible version
- `testament` (query, optional): Filter by testament ID (1=OT, 2=NT, 3=Apocrypha)

**Response:**
```json
[
  {
    "id": 1,
    "name": "Genesis",
    "abbreviation": "Gen",
    "testament_id": 1,
    "testament": "Old Testament"
  }
]
```

#### GET /list/books/antiguo
Shortcut for Old Testament books.

#### GET /list/books/nuevo
Shortcut for New Testament books.

#### GET /info/chapters/{libro_id}
Returns chapter count for a book.

**Response:**
```json
{ "total": 50 }
```

#### GET /info/verses/{libro_id}/{chapter}
Returns verse count for a chapter.

**Response:**
```json
{ "total": 31 }
```

#### GET /{libro}/{capitulo}
Returns all verses from a chapter by book name.

**Parameters:**
- `libro` (path): Book name or abbreviation (accent/case insensitive)
- `capitulo` (path): Chapter number
- `version` (query, optional): Bible version

**Response:**
```json
[
  {
    "id": 1,
    "book_id": 1,
    "book_name": "Genesis",
    "chapter": 1,
    "verse": 1,
    "text": "En el principio creo Dios los cielos y la tierra.",
    "version": "rvr1960"
  }
]
```

#### GET /bible/{book_id}/{chapter}
Returns all verses from a chapter by book ID.

#### GET /{libro}/{capitulo}/{versiculo}
Returns a specific verse.

**Response:**
```json
{
  "id": 26137,
  "book_id": 43,
  "book_name": "Juan",
  "chapter": 3,
  "verse": 16,
  "text": "Porque de tal manera amo Dios al mundo...",
  "version": "rvr1960"
}
```

#### GET /{libro}/{capitulo}/{versiculo}/{version}
Returns a specific verse in specified version.

#### GET /search/{query}
Searches Bible text (accent/case insensitive).

**Parameters:**
- `query` (path): Search text (URL encoded)
- `version` (query, optional): Bible version

**Response:**
```json
{
  "busqueda": "amor",
  "cantidad": 30,
  "resultados": [
    {
      "id": 251,
      "book_id": 1,
      "book_name": "Genesis",
      "chapter": 10,
      "verse": 16,
      "text": "al jebuseo, al amorreo, al gergeseo,",
      "version": "rvr1960"
    }
  ]
}
```

**Note:** Maximum 30 results returned.

### Radio Streaming Endpoints

#### GET /stream
Returns all registered radio stations.

**Response:**
```json
[
  {
    "id": 5,
    "nombre": "Enlace Juvenil-CR",
    "url_stream": "http://stream.zeno.fm/52hf40q405quv/;",
    "pais": "Costa Rica 88.4FM",
    "genero": "Cristiana",
    "logo_url": "https://cdn.instant.audio/images/logos/radios-co-cr/enlace-juvenil.png",
    "status": "online"
  }
]
```

#### POST /stream/add
Adds a new radio station.

**Request Body:**
```json
{
  "nombre": "Radio Aleluya",
  "url_stream": "http://servidor.com:8000/stream",
  "pais": "Costa Rica",
  "genero": "Cristiana",
  "logo_url": "https://ejemplo.com/logo.png",
  "status": "online"
}
```

**Response:**
```json
{
  "status": "success",
  "id": 6,
  "mensaje": "Radio agregada"
}
```

#### PUT /stream/{radio_id}
Updates a radio station.

**Response:**
```json
{ "mensaje": "Radio actualizada" }
```

#### DELETE /stream/{radio_id}
Deletes a radio station.

**Response:**
```json
{ "mensaje": "Radio eliminada" }
```

### Video Endpoints

#### GET /videos
Returns all registered videos.

**Response:**
```json
[
  {
    "id": 37,
    "video_id": "PjYcsu7EnJE",
    "titulo": "Rio de Vida",
    "canal_autor": "ELOI",
    "tipo": "video",
    "miniatura_url": "https://i.ytimg.com/vi/PjYcsu7EnJE/hqdefault.jpg",
    "fecha_registro": "2026-06-07 20:22:35"
  }
]
```

#### POST /videos/add
Registers a YouTube video (auto-extracts metadata).

**Parameters:**
- `url` (query): Full YouTube URL

**Response:**
```json
{
  "status": "success",
  "id": 38,
  "video_id": "PjYcsu7EnJE"
}
```

#### PUT /videos/{id}
Updates video metadata.

**Request Body:**
```json
{
  "id": 37,
  "video_id": "PjYcsu7EnJE",
  "titulo": "Nuevo Titulo",
  "canal_autor": "Nuevo Canal",
  "tipo": "video",
  "miniatura_url": "https://nueva-url.com/thumb.jpg"
}
```

**Response:**
```json
{ "mensaje": "Video actualizado" }
```

#### DELETE /videos/{id}
Deletes a video.

**Response:**
```json
{ "mensaje": "Video eliminado" }
```

## Data Models

### BibleVerse
```typescript
interface BibleVerse {
  id: number;
  book_id: number;
  book_name: string;
  chapter: number;
  verse: number;
  text: string;
  version: string;
}
```

### Book
```typescript
interface Book {
  id: number;
  name: string;
  abbreviation: string;
  testament_id: number;
  testament: string;
}
```

### RadioStream
```typescript
interface RadioStream {
  id: number;
  nombre: string;
  url_stream: string;
  pais: string;
  genero: string;
  logo_url: string | null;
  status: string;
}
```

### Video
```typescript
interface Video {
  id: number;
  video_id: string;
  titulo: string;
  canal_autor: string | null;
  tipo: string;
  miniatura_url: string | null;
  fecha_registro: string | null;
}
```

## Error Handling

All errors return JSON with a `detail` field:

```json
{
  "detail": "Libro 'invalido' no encontrado"
}
```

**HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `500`: Internal Server Error

## Usage Examples

### JavaScript/TypeScript
```typescript
// Get daily verse
const verse = await fetch('/daily/nvi').then(r => r.json());

// Search Bible
const results = await fetch('/search/amor?version=nvi').then(r => r.json());

// Get chapter
const chapter = await fetch('/genesis/1').then(r => r.json());

// Get specific verse
const verse = await fetch('/juan/3/16/nvi').then(r => r.json());
```

### Python
```python
import requests

# Get daily verse
verse = requests.get('/daily/nvi').json()

# Search Bible
results = requests.get('/search/amor?version=nvi').json()

# Get chapter
chapter = requests.get('/genesis/1').json()

# Get specific verse
verse = requests.get('/juan/3/16/nvi').json()
```

### cURL
```bash
# Daily verse
curl /daily/nvi

# Search
curl "/search/amor?version=nvi"

# Chapter
curl /genesis/1

# Verse
curl /juan/3/16/nvi
```

## Special Features

- **Accent-insensitive search**: "amor" finds "amo", "amo" finds "amor"
- **Case-insensitive**: All searches are case-insensitive
- **Flexible book names**: Use full name or abbreviation (e.g., "genesis" or "gen")
- **Multiple versions**: 8 Spanish Bible translations available

## Rate Limiting

- GET endpoints: No limit
- POST/PUT/DELETE: 60 requests per minute

## Admin Interface

Access the admin UI at `/admin` for managing radios and videos without code.

## Documentation

Full interactive documentation available at `/documentation`.
