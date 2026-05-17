import sqlite3
import random
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager
import libsql
from app.db.models import RadioStream, Video, normalizar, Verso


class BibliaEngine:
    def __init__(self, versions_config: Dict[str, str]):
        self.versions = versions_config
        self.default_version = "rvr1960"

    @contextmanager
    def _get_connection(self, version_id: Optional[str] = None):
        v_id = version_id or self.default_version
        conn = sqlite3.connect(self.versions[v_id])
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    
    def obtener_libros(self, version: Optional[str] = None, testament_id: Optional[int] = None) -> List[Dict]:
        """Retorna lista de libros con corrección dinámica de testamento."""
        with self._get_connection(version) as conn:
            cursor = conn.cursor()
            
            # Cargamos nombres de testamentos para mapear
            cursor.execute("SELECT id, name FROM testament")
            test_names = {row['id']: row['name'] for row in cursor.fetchall()}
            
            # Obtenemos los libros
            cursor.execute("SELECT id, name, abbreviation, testament_id FROM book")
            books = []
            for row in cursor.fetchall():
                b = dict(row)
                
                # --- PARCHE DE INTEGRIDAD ---
                # Las bases de datos tienen un error: casi todos los libros dicen testament_id = 1
                # Corregimos según el canon estándar:
                correct_tid = b['testament_id']
                if 1 <= b['id'] <= 39:
                    correct_tid = 1 # Antiguo
                elif 40 <= b['id'] <= 66:
                    correct_tid = 2 # Nuevo
                elif b['id'] > 66:
                    correct_tid = 3 # Apócrifos/Deuterocanónicos
                
                b['testament_id'] = correct_tid
                b['testament'] = test_names.get(correct_tid, "Unknown")
                
                # Filtrado por testamento si se solicita
                if testament_id and b['testament_id'] != testament_id:
                    continue
                
                books.append(b)
            return books

    def obtener_testamentos(self, version: Optional[str] = None) -> List[Dict]:
        """Retorna la lista de testamentos (Antiguo, Nuevo, etc.)."""
        with self._get_connection(version) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM testament")
            return [dict(row) for row in cursor.fetchall()]

    def get_capitulo(self, libro_id: int, cap: int, version: Optional[str] = None) -> List[Verso]:
        """Obtiene todos los versículos de un capítulo."""
        v_activa = version or self.default_version
        with self._get_connection(v_activa) as conn:
            cursor = conn.cursor()
            query = """
                SELECT v.id, v.book_id, b.name, v.chapter, v.verse, v.text 
                FROM verse v JOIN book b ON v.book_id = b.id 
                WHERE v.book_id = ? AND v.chapter = ? ORDER BY v.verse
            """
            cursor.execute(query, (libro_id, cap))
            return [Verso(*row, version=v_activa) for row in cursor.fetchall()]


    def obtener_cantidad_capitulos(self, libro_id: int, version: Optional[str] = None) -> int:
        """Retorna el número máximo de capítulos de un libro."""
        v_activa = version or self.default_version
        with self._get_connection(v_activa) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(chapter) FROM verse WHERE book_id = ?", (libro_id,))
            res = cursor.fetchone()
            return res[0] if res[0] else 0

    def obtener_cantidad_versiculos(self, libro_id: int, chapter: int, version: Optional[str] = None) -> int:
        """Retorna el número máximo de versículos de un capítulo."""
        v_activa = version or self.default_version
        with self._get_connection(v_activa) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(verse) FROM verse WHERE book_id = ? AND chapter = ?", (libro_id, chapter))
            res = cursor.fetchone()
            return res[0] if res[0] else 0

    def get_verso(self, libro_id: int, cap: int, ver: int, version: Optional[str] = None) -> Optional[Verso]:
        """Obtiene un único versículo[cite: 1]."""
        v_activa = version or self.default_version
        with self._get_connection(v_activa) as conn:
            cursor = conn.cursor()
            query = """
                SELECT v.id, v.book_id, b.name, v.chapter, v.verse, v.text 
                FROM verse v JOIN book b ON v.book_id = b.id 
                WHERE v.book_id = ? AND v.chapter = ? AND v.verse = ?
            """
            cursor.execute(query, (libro_id, cap, ver))
            row = cursor.fetchone()
            return Verso(*row, version=v_activa) if row else None

    def get_pasaje_diario(self, version: Optional[str] = None) -> Verso:
        """Retorna un verso aleatorio que cambia cada día[cite: 1]."""
        v_activa = version or self.default_version
        # Usamos la fecha actual como semilla para el random
        seed = int(datetime.now().strftime("%Y%m%d"))
        random.seed(seed)
        with self._get_connection(v_activa) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM verse")
            total = cursor.fetchone()[0]
            random_id = random.randint(1, total)
            cursor.execute("""
                SELECT v.id, v.book_id, b.name, v.chapter, v.verse, v.text 
                FROM verse v JOIN book b ON v.book_id = b.id WHERE v.id = ?
            """, (random_id,))
            return Verso(*cursor.fetchone(), version=v_activa)

    def buscar_texto(self, query: str, version: Optional[str] = None) -> List[Verso]:
        """Busca coincidencias cercanas permitiendo palabras en cualquier orden[cite: 1, 3].
        """
        v_activa = version or self.default_version
        # 1. Normalizamos y dividimos en palabras (filtramos palabras de 1-2 letras para precisión)
        palabras = [normalizar(p) for p in query.split() if len(p) > 2]
        
        if not palabras:
            return []

        with self._get_connection(v_activa) as conn:
            conn.create_function("NORM", 1, normalizar)
            cursor = conn.cursor()
            
            # 2. Construimos dinámicamente el WHERE con múltiples LIKE
            # Resultado esperado: WHERE NORM(v.text) LIKE ? AND NORM(v.text) LIKE ? ...
            condiciones = " AND ".join(["NORM(v.text) LIKE ?" for _ in palabras])
            parametros = [f"%{p}%" for p in palabras]
            
            sql = f"""
                SELECT v.id, v.book_id, b.name, v.chapter, v.verse, v.text 
                FROM verse v 
                JOIN book b ON v.book_id = b.id 
                WHERE {condiciones}
                LIMIT 30
            """
            
            cursor.execute(sql, parametros)
            return [Verso(*row, version=v_activa) for row in cursor.fetchall()]
        
# Radios


class StreamManager:
    def __init__(self, db_url: str, auth_token: str):
        self.db_url = db_url
        self.auth_token = auth_token

    def _get_connection(self):
        return libsql.connect(self.db_url, auth_token=self.auth_token)

    def agregar_radio(self, radio: RadioStream) -> int:
        url = radio.url_stream.strip()
        if not url.endswith('/') and ":" in url:
            url += "/;"

        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO streams (nombre, url_stream, pais, genero, logo_url, status) VALUES (?, ?, ?, ?, ?, ?)",
                [radio.nombre, url, radio.pais, radio.genero, radio.logo_url, radio.status]
            )
            return cursor.last_insert_rowid

    def listar_radios(self) -> List[RadioStream]:
        with self._get_connection() as conn:
            result = conn.execute("SELECT * FROM streams ORDER BY nombre ASC")
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()
            return [RadioStream(**{col: val for col, val in zip(columns, row)}) for row in rows]

    def eliminar_radio(self, radio_id: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM streams WHERE id = ?", [radio_id])
            return cursor.rowcount > 0

    def editar_radio(self, radio_id: int, radio: RadioStream) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE streams SET nombre = ?, url_stream = ?, pais = ?, genero = ?, logo_url = ?, status = ? WHERE id = ?",
                [radio.nombre, radio.url_stream, radio.pais, radio.genero, radio.logo_url, radio.status, radio_id]
            )
            return cursor.rowcount > 0
        

# NOTA: En este archivo se definen las clases que interactúan directamente con las bases de datos SQLite, tanto para la Biblia como para las radios. Estas clases encapsulan toda la lógica de acceso a datos, permitiendo que el resto de la aplicación (como los endpoints en main.py) se mantenga limpio y enfocado en la lógica de negocio.

# Creare la clase VideoManager para manejar los videos que se suban a la base de datos cumpliendo la funciones crud, los datos se enviaran solo con la url del video y el sistema se encargara de extraer 
# CREATE TABLE IF NOT EXISTS videos (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     video_id TEXT NOT NULL UNIQUE,       -- ID extraído de la URL (ej: CpER8t9JDTI)
#     titulo TEXT NOT NULL,                -- Mapea a "title"
#     canal_autor TEXT,                    -- Mapea a "author_name"
#     tipo TEXT,                           -- Mapea a "type" (usualmente 'video')
#     miniatura_url TEXT,                  -- Mapea a "thumbnail_url"
#     fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
# );


# INSERT INTO videos (video_id, titulo, canal_autor, tipo, miniatura_url) 
# VALUES (
#     'CpER8t9JDTI', 
#     '¡Felicidades! Sólo el 1% recibe esta Canción Profética de Oración que Cambia Vidas (No la ignores)', 
#     'Salmos En Canción', 
#     'video', 
#     'https://i.ytimg.com/vi/CpER8t9JDTI/hqdefault.jpg'
# );

# Al final de app/db/database.py

class VideoManager:
    def __init__(self, db_url: str, auth_token: str):
        self.db_url = db_url
        self.auth_token = auth_token

    def _get_connection(self):
        return libsql.connect(self.db_url, auth_token=self.auth_token)

    def agregar_video(self, video: Video) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT OR IGNORE INTO videos (video_id, titulo, canal_autor, tipo, miniatura_url) VALUES (?, ?, ?, ?, ?)",
                [video.video_id, video.titulo, video.canal_autor, video.tipo, video.miniatura_url]
            )
            return cursor.last_insert_rowid

    def listar_videos(self) -> List[Video]:
        with self._get_connection() as conn:
            result = conn.execute("SELECT * FROM videos ORDER BY fecha_registro DESC")
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()
            return [Video(**{col: val for col, val in zip(columns, row)}) for row in rows]

    def eliminar_video(self, video_id_db: int) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM videos WHERE id = ?", [video_id_db])
            return cursor.rowcount > 0

    def editar_video(self, id_db: int, video: Video) -> bool:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "UPDATE videos SET titulo = ?, canal_autor = ?, miniatura_url = ? WHERE id = ?",
                [video.titulo, video.canal_autor, video.miniatura_url, id_db]
            )
            return cursor.rowcount > 0
        
