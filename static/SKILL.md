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

### API Info Endpoints

#### GET /api-info
Returns complete API metadata as JSON, including available Bible versions and their file paths.

**Response:**
```json
{
  "nombre": "GhostRoot Bible API",
  "version": "1.0.0",
  "biblias": {
    "rvr1960": "app/files/rvr1960.sqlite",
    "nvi": "app/files/NVI1999.sqlite"
  }
}
```

#### GET /download/skill
Downloads this SKILL.md file for integration with AI assistants.

**Response:** Markdown file attachment.

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

#### GET /random
Returns a completely random verse (changes on every request, no daily seed).

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

#### GET /books/{book_id}
Returns a single Bible book by its numeric ID.

**Parameters:**
- `version` (query, optional): Bible version

**Response:**
```json
{
  "id": 1,
  "name": "Genesis",
  "abbreviation": "Gen",
  "testament_id": 1,
  "testament": "Old Testament"
}
```

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
- `limit` (query, optional): Results per page (default: 30, max: 100)
- `offset` (query, optional): Pagination offset (default: 0)

**Response:**
```json
{
  "busqueda": "amor",
  "cantidad": 30,
  "total": 142,
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

**Note:** Words of 1-2 characters are automatically filtered out for accuracy. Use `limit` and `offset` for pagination.

### Radio Streaming Endpoints

#### GET /stream
Returns all registered radio stations.

**Parameters:**
- `page` (query, optional): Page number (enables paginated response)
- `limit` (query, optional): Items per page when paginated (default: 20, max: 100)

**Response (all):**
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

**Response (paginated):**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 5,
    "pages": 1
  }
}
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

### Video / Audio Endpoints

Supports both **YouTube videos** and **Spotify tracks**. The API auto-detects the URL type.

#### GET /videos
Returns all registered videos and audio tracks.

**Parameters:**
- `page` (query, optional): Page number (enables paginated response)
- `limit` (query, optional): Items per page when paginated (default: 20, max: 100)

**Response (all):**
```json
[
  {
    "id": 37,
    "video_id": "PjYcsu7EnJE",
    "titulo": "Rio de Vida",
    "canal_autor": "ELOI",
    "tipo": "youtube",
    "miniatura_url": "https://i.ytimg.com/vi/PjYcsu7EnJE/hqdefault.jpg",
    "fecha_registro": "2026-06-07 20:22:35",
    "embed_url": "https://www.youtube.com/embed/PjYcsu7EnJE",
    "player_url": "https://www.youtube.com/watch?v=PjYcsu7EnJE"
  },
  {
    "id": 42,
    "video_id": "69hFBsRNHaKuCkraGiExgA",
    "titulo": "Cuando Yo Te Conocí",
    "canal_autor": "Artista",
    "tipo": "spotify",
    "miniatura_url": "https://i.scdn.co/image/...",
    "fecha_registro": "2026-06-16 14:50:23",
    "embed_url": "https://open.spotify.com/embed/track/69hFBsRNHaKuCkraGiExgA",
    "player_url": "https://open.spotify.com/track/69hFBsRNHaKuCkraGiExgA"
  }
]
```

**Response (paginated):**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 50,
    "pages": 3
  }
}
```

**Fields:**
- `tipo`: `"youtube"` | `"spotify"` — use to determine player type
- `embed_url`: URL for iframe embedding (YouTube embed or Spotify widget)
- `player_url`: Direct link to the content on the native platform

#### POST /videos/add
Registers a **single** YouTube video or Spotify track (auto-detects URL type, extracts metadata via oembed).

**Parameters:**
- `url` (query): YouTube URL (`youtube.com/watch?v=...`, `youtu.be/...`) **or** Spotify URL (`open.spotify.com/track/...`)

**Response (success):**
```json
{
  "status": "success",
  "id": 38,
  "video_id": "PjYcsu7EnJE"
}
```

**Response (duplicate):**
```json
{
  "detail": "El video 'PjYcsu7EnJE' ya existe en la base de datos"
}
```
Status code: `409 Conflict`

#### POST /videos/import
Imports **multiple** videos from a YouTube channel or playlist. Uses `yt-dlp` (no API keys needed).

**Supported URLs:**
- YouTube playlist: `youtube.com/playlist?list=...`
- YouTube channel: `youtube.com/@handle` or `youtube.com/channel/{id}`
- YouTube custom URL: `youtube.com/c/name` or `youtube.com/user/name`

**Parameters:**
- `url` (query): Channel/playlist URL

**Response:**
```json
{
  "status": "success",
  "type": "playlist",
  "source_id": "PLHuD7OrIIOz...",
  "imported": 12,
  "skipped": 3,
  "items": [
    { "id": 42, "video_id": "dQw4w9WgXcQ" }
  ]
}
```

- `imported`: videos nuevos agregados
- `skipped`: videos que ya existían (omitidos automáticamente)

**Note:** Sin configuración — funciona con `yt-dlp`. Máximo 50 videos.

#### POST /videos/import/preview
Returns a list of videos from a collection **without importing them**. Use this to let users select which videos to import.

**Request Body:**
```json
{
  "url": "https://youtube.com/playlist?list=PLK13vpeAIKd..."
}
```

**Response:**
```json
{
  "url": "https://youtube.com/playlist?list=PLK13vpeAIKd...",
  "total": 15,
  "videos": [
    {
      "video_id": "dQw4w9WgXcQ",
      "titulo": "Título del video",
      "canal_autor": "Nombre del canal",
      "miniatura_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"
    }
  ]
}
```

#### POST /videos/import/selected
Importa solo los videos seleccionados después de una vista previa.

**Request Body:**
```json
{
  "videos": [
    {
      "video_id": "dQw4w9WgXcQ",
      "titulo": "Título del video",
      "canal_autor": "Nombre del canal",
      "miniatura_url": "https://i.ytimg.com/vi/.../hqdefault.jpg"
    }
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "imported": 5,
  "skipped": 1,
  "items": [{ "id": 42, "video_id": "dQw4w9WgXcQ" }]
}
```

#### PUT /videos/{id}
Updates video/audio metadata.

**Request Body:**
```json
{
  "id": 37,
  "video_id": "PjYcsu7EnJE",
  "titulo": "Nuevo Titulo",
  "canal_autor": "Nuevo Canal",
  "tipo": "youtube",
  "miniatura_url": "https://nueva-url.com/thumb.jpg"
}
```

#### DELETE /videos/{id}
Deletes a video or audio track.

**Response:**
```json
{ "mensaje": "Video eliminado" }
```

### Real-Time via WebSocket

All mutations to streams and videos are broadcast in real-time to connected clients.

#### GET /ws/{channel}
Upgrades to a WebSocket connection.

**Channels:**
- `videos` — receives `video:created`, `video:updated`, `video:deleted` events
- `streams` — receives `stream:created`, `stream:updated`, `stream:deleted` events
- `biblia` — receives `guide:created`, `guide:updated`, `guide:deleted` events

**Event format:**
```json
{
  "type": "video:created",
  "data": { "id": 38, "titulo": "...", "tipo": "youtube", ... }
}
```

**Client example:**
```javascript
const ws = new WebSocket('wss://api-biblia-py.onrender.com/ws/videos');
ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  // msg.type: "video:created" | "video:updated" | "video:deleted"
  // msg.data: the affected resource
};
```

**Keep-alive:** Send `"ping"` — server replies `"pong"`. Auto-reconnect recommended.

### Study Guide Endpoints

Guías de estudio bíblico con referencias cruzadas a versículos. El contenido se renderiza como HTML con markdown y las referencias bíblicas se convierten en enlaces clickeables que apuntan directamente al versículo (ej: `/2 corintios/3/18`).

#### GET /guide
Returns paginated study guides. Optional `?tag=` filter.

**Parameters:**
- `tag` (query, optional): Filter by tag
- `page` (query, optional): Page number (default: 1)
- `limit` (query, optional): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "title": "Guía de Estudio Bíblico Integral",
      "author": "Teólogo, historiador bíblico y pastor",
      "tags": "discipulado, oracion, fe, gracia, santidad",
      "tag_list": ["discipulado", "oracion", "fe"],
      "status": "published",
      "created_at": "2026-06-29 12:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "pages": 1
  }
}
```

**Caching:** Response includes `ETag` and `Cache-Control: max-age=60` headers.

#### GET /guide/tags
Returns all available tags.

**Response:**
```json
["discipulado", "oracion", "fe", "santidad", "iglesia"]
```

#### GET /guide/{id}
Returns full guide with parsed Bible references.

**Parameters:**
- `html` (query, optional): Set to `true` to get content with Bible refs as HTML links

**Response:**
```json
{
  "id": 1,
  "title": "Guía de Estudio Bíblico Integral",
  "content": "...",
  "versiculos": [
    {
      "book_id": 48,
      "book_name": "Gálatas",
      "chapter": 4,
      "verse_start": 19,
      "reference": "Gálatas 4:19"
    }
  ],
  "content_html": "<p>... <a href=\"/galatas/4/19\" class=\"bible-ref\">Gálatas 4:19</a> ...</p>"
}
```

**Note:** `content_html` is pre-computed and cached in the database for performance. Bible reference links use spaces in book names (e.g., `/2 corintios/3/18`), which browsers encode as `%20`.

**Caching:** Response includes `ETag` and `Cache-Control: max-age=60` headers.

#### GET /guide/{id}/verses
Returns full Bible verses for all references in the guide (batch lookup, deduplicates references).

**Parameters:**
- `version` (query, optional): Bible version code

**Response:**
```json
[
  {
    "book_name": "Gálatas",
    "chapter": 4,
    "verse": 19,
    "text": "Hijitos míos, por quienes vuelvo a sufrir dolores de parto...",
    "version": "rvr1960"
  }
]
```

#### POST /guide/add
Creates a new study guide. Tags auto-extracted from content if not provided. `content_html` is pre-computed on creation.

**Request Body:**
```json
{
  "id": null,
  "title": "Guía de Estudio Bíblico Integral",
  "author": "Autor",
  "content": "Texto completo de la guía...",
  "tags": "discipulado, oracion, fe",
  "status": "published"
}
```

#### PUT /guide/{id}
Updates a study guide. Re-computes `content_html` cache.

#### DELETE /guide/{id}
Deletes a study guide.

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

### Video / Audio
```typescript
interface Video {
  id: number;
  video_id: string;
  titulo: string;
  canal_autor: string | null;
  tipo: "youtube" | "spotify";
  miniatura_url: string | null;
  fecha_registro: string | null;
  embed_url: string;   // URL for iframe embedding
  player_url: string;  // Direct link to platform
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
- `409`: Conflict (duplicate video)
- `422`: Validation Error (FastAPI)
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
- **Auto-corrección de caracteres RTF**: Los textos bíblicos se limpian automáticamente de códigos RTF y escapes hexadecimales (ej: `\'e1` → `á`)
- **Parcheo de testament_id**: Los IDs de testamento se corrigen dinámicamente según el canon estándar (1-39: AT, 40-66: NT, 66+: Apócrifos)
- **Auto-extracción de tags**: Si no se proporcionan tags al crear una guía de estudio, se extraen automáticamente del contenido
- **Auto-corrección URL streaming**: Las URLs de streaming se normalizan agregando `;/` al final si falta
- **Filtro de palabras cortas**: En búsquedas, palabras de 1-2 caracteres se filtran automáticamente para mejorar precisión

## Rate Limiting

- All endpoints: 120 requests per minute per IP
- Exceeded requests return `429 Too Many Requests` with `Retry-After` header

## Caching Strategy

- **ETag headers:** All guide endpoints return `ETag` and `Cache-Control: max-age=60`
- **Client-side caching:** Send `If-None-Match` header with the ETag value to receive `304 Not Modified` when content hasn't changed
- **Server-side caching:** `content_html` is pre-computed and cached in the database on guide creation/update
- **GZip compression:** Responses > 500 bytes are automatically compressed

## Performance Optimizations

- **Pagination:** Guide listings return paginated results (default: 20 items, max: 100)
- **Batch verse lookup:** `/guide/{id}/verses` deduplicates references and fetches all verses in a single pass
- **Database indexes:** Optimized queries on `status`, `created_at`, and `guide_tags`
- **Pre-computed HTML:** Markdown rendering and Bible reference linking happens once on write, not on every read

## Admin Interface

Access the admin UI at `/admin` for managing radios and videos without code.

## Documentation

Full interactive documentation is served from the VitePress build at `/docs-ui/`.

If the docs page loads without CSS/JS, verify:
- `docs-ui/docs/.vitepress/config.mjs` has `base: '/docs-ui/'`
- the FastAPI app mounts the generated VitePress dist under `/docs-ui`
- legacy `docs-ui/index.html` does not conflict with the built site

## Brand Assets

Official GhostRoot Bible API icons available for public use:

- **SVG**: `/static/img/icon.svg` (Scalable, ideal for web and apps)
- **JPG**: `/static/img/icon.jpg` (Universal compatibility, ideal for previews)

These icons are free to use for linking to this API, in your documentation, or to represent your integration with GhostRoot Bible API.
