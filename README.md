# 📖 Guía Oficial: API GhostRoot Bible

Bienvenido a la documentación oficial de **GhostRoot Bible API**, una solución de alto rendimiento para la gestión, exploración y estudio de las Sagradas Escrituras y contenido multimedia cristiano.

---

## 🛠️ Arquitectura y Tecnologías

- **Lenguaje**: Python 3.9+
- **Framework**: FastAPI (Asíncrono y ultra-rápido)
- **Base de Datos**: SQLite (múltiples archivos para diferentes versiones)
- **Multimedia**: Gestión de Radio Streaming y Videos de YouTube integrada.
- **Limpieza de Datos**: Procesador dinámico para eliminar RTF y decodificar caracteres especiales heredados.

---

## 🧭 Referencia Completa de Endpoints

### 📖 Biblia y Canon
| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/` | Lista de versiones instaladas. |
| `GET` | `/daily` | Versículo diario aleatorio por fecha. |
| `GET` | `/list/testaments` | Lista de testamentos (Antiguo/Nuevo). |
| `GET` | `/list/books` | Lista de libros (filtro opcional `?testament=id`). |
| `GET` | `/list/books/antiguo` | Libros del Antiguo Testamento. |
| `GET` | `/list/books/nuevo` | Libros del Nuevo Testamento. |
| `GET` | `/bible/{id}/{ch}` | Capítulos completos por ID de libro. |
| `GET` | `/{libro}/{ch}` | Capítulos completos por nombre. |
| `GET` | `/search/{query}` | Búsqueda global (insensible a tildes). |

### 📻 Streaming (Radio)
| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/stream` | Listar todas las radios. |
| `POST` | `/stream/add` | Agregar nueva radio. |
| `PUT` | `/stream/{id}` | Editar datos de una radio. |
| `DELETE` | `/stream/{id}` | Eliminar una radio. |

### 📺 Multimedia (Videos)
| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/videos` | Listar videos registrados. |
| `POST` | `/videos/add` | Agregar video (automático desde URL). |
| `PUT` | `/videos/{id}` | Editar metadatos del video. |
| `DELETE` | `/videos/{id}` | Eliminar video. |

---

## 💡 Modelos de Datos para Escritura

### RadioStream (Para Agregar/Editar)
Para agregar una radio (`POST /stream/add`), debes enviar un JSON con los siguientes campos:
- `nombre`: Nombre de la estación (ej: "Radio Aleluya").
- `url_stream`: URL del streaming (ej: `http://servidor.com:8000/stream`).
- `pais`: País de origen.
- `genero`: Género (ej: "Cristiana", "Adoración").
- `logo_url`: URL de la imagen del logo.
- `status`: `1` para activo, `0` para inactivo.

### Video (Para Editar)
Para editar un video (`PUT /videos/{id}`), puedes actualizar:
- `titulo`: Título personalizado.
- `canal_autor`: Nombre del canal o autor.
- `miniatura_url`: URL de la imagen de previsualización.

---

## 🚀 Ejemplos de Consumo Profesional

### ⚛️ React / Next.js (Admin: Agregar Radio)
```javascript
const addRadio = async (radioData) => {
  const res = await fetch("https://api.tu-dominio.com/stream/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(radioData)
  });
  const result = await res.json();
  if (result.status === "success") alert("Radio agregada con éxito!");
};
```

### 🐍 Python (Admin: Agregar Video por URL)
```python
import requests

def registrar_video_youtube(url_youtube):
    url_api = "https://api.tu-dominio.com/videos/add"
    # El sistema extrae automáticamente el ID, título y miniatura
    response = requests.post(url_api, params={"url": url_youtube})
    if response.status_code == 200:
        print("Video registrado exitosamente:", response.json())

registrar_video_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
```

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/anonymous-sys19/API-BIBLIA-PY)
---
© 2026 GhostRoot Bible Project. Desarrollado para la excelencia en la difusión de la Palabra.
