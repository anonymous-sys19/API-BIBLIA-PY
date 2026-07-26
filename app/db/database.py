import sqlite3
import random
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager
import libsql
from app.db.models import RadioStream, Video, GuiaEstudio, normalizar, Verso
from app.services.bible_ref import marcar_referencias_html, parse_referencia


class BibliaEngine:
    def __init__(self, versions_config: Dict[str, str]):
        self.versions = versions_config
        self.default_version = "rvr1960"

    @contextmanager
    def _get_connection(self, version_id: Optional[str] = None):
        v_id = (version_id or self.default_version).lower()
        if v_id not in self.versions:
            v_id = self.default_version
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

    def obtener_libro_por_id(self, book_id: int, version: Optional[str] = None) -> Optional[Dict]:
        """Retorna un libro individual por su ID con corrección de testamento."""
        with self._get_connection(version) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM testament")
            test_names = {row['id']: row['name'] for row in cursor.fetchall()}
            cursor.execute("SELECT id, name, abbreviation, testament_id FROM book WHERE id = ?", [book_id])
            row = cursor.fetchone()
            if not row:
                return None
            b = dict(row)
            correct_tid = b['testament_id']
            if 1 <= b['id'] <= 39:
                correct_tid = 1
            elif 40 <= b['id'] <= 66:
                correct_tid = 2
            elif b['id'] > 66:
                correct_tid = 3
            b['testament_id'] = correct_tid
            b['testament'] = test_names.get(correct_tid, "Unknown")
            return b

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

    def get_verso_aleatorio(self, version: Optional[str] = None) -> Verso:
        """Retorna un verso completamente aleatorio (sin semilla, cambia en cada llamado)."""
        v_activa = version or self.default_version
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

    def buscar_texto(self, query: str, version: Optional[str] = None, limit: int = 30, offset: int = 0) -> Tuple[List[Verso], int]:
        """Busca coincidencias cercanas permitiendo palabras en cualquier orden[cite: 1, 3].
        Retorna (resultados, total_count).
        """
        v_activa = version or self.default_version
        # 1. Normalizamos y dividimos en palabras (filtramos palabras de 1-2 letras para precisión)
        palabras = [normalizar(p) for p in query.split() if len(p) > 2]
        
        if not palabras:
            return [], 0

        with self._get_connection(v_activa) as conn:
            conn.create_function("NORM", 1, normalizar)
            cursor = conn.cursor()
            
            # 2. Construimos dinámicamente el WHERE con múltiples LIKE
            condiciones = " AND ".join(["NORM(v.text) LIKE ?" for _ in palabras])
            parametros = [f"%{p}%" for p in palabras]
            
            count_sql = f"""
                SELECT COUNT(*) 
                FROM verse v 
                JOIN book b ON v.book_id = b.id 
                WHERE {condiciones}
            """
            cursor.execute(count_sql, parametros)
            total = cursor.fetchone()[0]
            
            sql = f"""
                SELECT v.id, v.book_id, b.name, v.chapter, v.verse, v.text 
                FROM verse v 
                JOIN book b ON v.book_id = b.id 
                WHERE {condiciones}
                LIMIT ? OFFSET ?
            """
            
            cursor.execute(sql, parametros + [limit, offset])
            return [Verso(*row, version=v_activa) for row in cursor.fetchall()], total
        
# Radios


class StreamManager:
    def __init__(self, db_url: str, auth_token: str):
        self.db_url = db_url
        self.auth_token = auth_token

    def _get_connection(self):
        return libsql.connect(self.db_url, auth_token=self.auth_token) # type: ignore

    def agregar_radio(self, radio: RadioStream) -> int:
        url = radio.url_stream.strip()
        if not url.endswith('/') and ":" in url:
            url += "/;"

        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO streams (nombre, url_stream, pais, genero, logo_url, status) VALUES (?, ?, ?, ?, ?, ?)",
                [radio.nombre, url, radio.pais, radio.genero, radio.logo_url, radio.status]
            )
            return cursor.lastrowid

    def listar_radios(self, limit: int = 0, offset: int = 0) -> List[RadioStream]:
        with self._get_connection() as conn:
            if limit > 0:
                result = conn.execute("SELECT * FROM streams ORDER BY nombre ASC LIMIT ? OFFSET ?", [limit, offset])
            else:
                result = conn.execute("SELECT * FROM streams ORDER BY nombre ASC")
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()
            return [RadioStream(**{col: val for col, val in zip(columns, row)}) for row in rows]

    def contar_radios(self) -> int:
        with self._get_connection() as conn:
            return conn.execute("SELECT COUNT(*) FROM streams").fetchone()[0]

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
        return libsql.connect(self.db_url, auth_token=self.auth_token) # type: ignore

    def agregar_video(self, video: Video) -> Optional[int]:
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT OR IGNORE INTO videos (video_id, titulo, canal_autor, tipo, miniatura_url) VALUES (?, ?, ?, ?, ?)",
                [video.video_id, video.titulo, video.canal_autor, video.tipo, video.miniatura_url]
            )
            if cursor.rowcount == 0:
                return None
            return cursor.lastrowid

    def listar_videos(self, limit: int = 0, offset: int = 0) -> List[Video]:
        with self._get_connection() as conn:
            if limit > 0:
                result = conn.execute("SELECT * FROM videos ORDER BY fecha_registro DESC LIMIT ? OFFSET ?", [limit, offset])
            else:
                result = conn.execute("SELECT * FROM videos ORDER BY fecha_registro DESC")
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()
            return [Video(**{col: val for col, val in zip(columns, row)}) for row in rows]

    def contar_videos(self) -> int:
        with self._get_connection() as conn:
            return conn.execute("SELECT COUNT(*) FROM videos").fetchone()[0]

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
        

class GuiaManager:
    def __init__(self, db_url: str, auth_token: str):
        self.db_url = db_url
        self.auth_token = auth_token
        self._init_db()

    def _get_connection(self):
        return libsql.connect(self.db_url, auth_token=self.auth_token) # type: ignore

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS study_guides (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT DEFAULT '',
                    content TEXT NOT NULL,
                    content_html TEXT DEFAULT '',
                    tags TEXT DEFAULT '',
                    cover_image TEXT DEFAULT '',
                    status TEXT DEFAULT 'published',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS guide_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guide_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    FOREIGN KEY (guide_id) REFERENCES study_guides(id) ON DELETE CASCADE
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_guides_status ON study_guides(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_guides_created ON study_guides(created_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_guide_tags_tag ON guide_tags(tag)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_guide_tags_guide_id ON guide_tags(guide_id)")
            
            try:
                conn.execute("ALTER TABLE study_guides ADD COLUMN content_html TEXT DEFAULT ''")
            except Exception:
                pass

    def listar_guias(self, page: int = 1, limit: int = 20) -> Tuple[List[Dict], int]:
        offset = (page - 1) * limit
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM study_guides").fetchone()[0]
            result = conn.execute(
                "SELECT id, title, author, tags, cover_image, status, created_at, updated_at FROM study_guides ORDER BY created_at DESC LIMIT ? OFFSET ?",
                [limit, offset]
            )
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()
            if not rows:
                return [], total
            guias = []
            guide_ids = [row[0] for row in rows]
            placeholders = ",".join("?" * len(guide_ids))
            tags_result = conn.execute(
                f"SELECT guide_id, tag FROM guide_tags WHERE guide_id IN ({placeholders})",
                guide_ids
            )
            tags_map = {}
            for gid, tag in tags_result.fetchall():
                tags_map.setdefault(gid, []).append(tag)
            for row in rows:
                g = {col: val for col, val in zip(columns, row)}
                g["tag_list"] = tags_map.get(g["id"], [])
                guias.append(g)
            return guias, total

    def obtener_guia(self, guia_id: int) -> Optional[Dict]:
        with self._get_connection() as conn:
            result = conn.execute("SELECT * FROM study_guides WHERE id = ?", [guia_id])
            row = result.fetchone()
            if not row:
                return None
            columns = [desc[0] for desc in result.description]
            g = {col: val for col, val in zip(columns, row)}
            tags_result = conn.execute("SELECT tag FROM guide_tags WHERE guide_id = ?", [guia_id])
            g["tag_list"] = [r[0] for r in tags_result.fetchall()]
            if not g.get("content_html"):
                g["content_html"] = marcar_referencias_html(g["content"])
                conn.execute("UPDATE study_guides SET content_html = ? WHERE id = ?", [g["content_html"], guia_id])
            return g

    def agregar_guia(self, guia: GuiaEstudio) -> Optional[int]:
        content_html = marcar_referencias_html(guia.content)
        with self._get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO study_guides (title, author, content, content_html, tags, cover_image, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                [guia.title, guia.author, guia.content, content_html, guia.tags, guia.cover_image, guia.status]
            )
            guia_id = cursor.lastrowid
            self._sync_tags(conn, guia_id, guia.tags)
            return guia_id

    def editar_guia(self, guia_id: int, guia: GuiaEstudio) -> bool:
        content_html = marcar_referencias_html(guia.content)
        with self._get_connection() as conn:
            cursor = conn.execute(
                """UPDATE study_guides 
                   SET title = ?, author = ?, content = ?, content_html = ?, tags = ?, cover_image = ?, status = ?, updated_at = CURRENT_TIMESTAMP 
                   WHERE id = ?""",
                [guia.title, guia.author, guia.content, content_html, guia.tags, guia.cover_image, guia.status, guia_id]
            )
            if cursor.rowcount > 0:
                self._sync_tags(conn, guia_id, guia.tags)
                return True
            return False

    def eliminar_guia(self, guia_id: int) -> bool:
        with self._get_connection() as conn:
            conn.execute("DELETE FROM guide_tags WHERE guide_id = ?", [guia_id])
            cursor = conn.execute("DELETE FROM study_guides WHERE id = ?", [guia_id])
            return cursor.rowcount > 0

    def _sync_tags(self, conn, guia_id: int, tags_str: str):
        conn.execute("DELETE FROM guide_tags WHERE guide_id = ?", [guia_id])
        if not tags_str:
            return
        tags = [t.strip().lower() for t in tags_str.split(",") if t.strip()]
        if tags:
            conn.executemany(
                "INSERT INTO guide_tags (guide_id, tag) VALUES (?, ?)",
                [(guia_id, tag) for tag in tags]
            )

    def buscar_por_tag(self, tag: str, page: int = 1, limit: int = 20) -> Tuple[List[Dict], int]:
        offset = (page - 1) * limit
        with self._get_connection() as conn:
            total = conn.execute(
                "SELECT COUNT(DISTINCT sg.id) FROM study_guides sg JOIN guide_tags gt ON sg.id = gt.guide_id WHERE gt.tag = ? AND sg.status = 'published'",
                [tag.lower()]
            ).fetchone()[0]
            result = conn.execute(
                """SELECT sg.id, sg.title, sg.author, sg.tags, sg.cover_image, sg.status, sg.created_at, sg.updated_at
                   FROM study_guides sg
                   JOIN guide_tags gt ON sg.id = gt.guide_id
                   WHERE gt.tag = ? AND sg.status = 'published'
                   ORDER BY sg.created_at DESC
                   LIMIT ? OFFSET ?""",
                [tag.lower(), limit, offset]
            )
            columns = [desc[0] for desc in result.description]
            rows = result.fetchall()
            if not rows:
                return [], total
            guide_ids = [row[0] for row in rows]
            placeholders = ",".join("?" * len(guide_ids))
            tags_result = conn.execute(
                f"SELECT guide_id, tag FROM guide_tags WHERE guide_id IN ({placeholders})",
                guide_ids
            )
            tags_map = {}
            for gid, t in tags_result.fetchall():
                tags_map.setdefault(gid, []).append(t)
            guias = []
            for row in rows:
                g = {col: val for col, val in zip(columns, row)}
                g["tag_list"] = tags_map.get(g["id"], [])
                guias.append(g)
            return guias, total

    def listar_tags(self) -> List[str]:
        with self._get_connection() as conn:
            result = conn.execute("SELECT DISTINCT tag FROM guide_tags ORDER BY tag ASC")
            return [r[0] for r in result.fetchall()]
