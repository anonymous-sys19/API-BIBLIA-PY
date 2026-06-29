import re
import markdown
from typing import List, Dict, Optional, Tuple

LIBROS_BIBLICOS = {
    "Génesis": 1, "Genesis": 1, "Gen": 1, "Gn": 1,
    "Éxodo": 2, "Exodo": 2, "Ex": 2,
    "Levítico": 3, "Levitico": 3, "Lv": 3, "Lev": 3,
    "Números": 4, "Numeros": 4, "Nm": 4, "Num": 4,
    "Deuteronomio": 5, "Dt": 5, "Deu": 5,
    "Josué": 6, "Josue": 6, "Jos": 6,
    "Jueces": 7, "Jue": 7, "Jc": 7,
    "Rut": 8,
    "1 Samuel": 9, "1 Sam": 9, "1Sa": 9,
    "2 Samuel": 10, "2 Sam": 10, "2Sa": 10,
    "1 Reyes": 11, "1 Re": 11, "1Re": 11,
    "2 Reyes": 12, "2 Re": 12, "2Re": 12,
    "1 Crónicas": 13, "1 Cronicas": 13, "1 Cr": 13, "1Cro": 13,
    "2 Crónicas": 14, "2 Cronicas": 14, "2 Cr": 14, "2Cro": 14,
    "Esdras": 15, "Esd": 15,
    "Nehemías": 16, "Nehemias": 16, "Neh": 16,
    "Ester": 17, "Est": 17,
    "Job": 18,
    "Salmos": 19, "Sal": 19, "Sl": 19,
    "Proverbios": 20, "Prv": 20, "Pr": 20, "Pro": 20,
    "Eclesiastés": 21, "Eclesiastes": 21, "Ec": 21, "Ecl": 21,
    "Cantares": 22, "Cnt": 22, "Cant": 22,
    "Isaías": 23, "Isaias": 23, "Is": 23, "Isa": 23,
    "Jeremías": 24, "Jeremias": 24, "Jer": 24, "Jr": 24,
    "Lamentaciones": 25, "Lam": 25, "Lm": 25,
    "Ezequiel": 26, "Ez": 26, "Eze": 26,
    "Daniel": 27, "Dan": 27, "Dn": 27,
    "Oseas": 28, "Os": 28,
    "Joel": 29, "Jl": 29,
    "Amós": 30, "Amos": 30, "Am": 30,
    "Abdías": 31, "Abdias": 31, "Abd": 31,
    "Jonás": 32, "Jonas": 32, "Jon": 32,
    "Miqueas": 33, "Miq": 33,
    "Nahúm": 34, "Nahum": 34, "Nah": 34,
    "Habacuc": 35, "Hab": 35,
    "Sofonías": 36, "Sofonias": 36, "Sof": 36,
    "Hageo": 37, "Hag": 37,
    "Zacarías": 38, "Zacarias": 38, "Zac": 38,
    "Malaquías": 39, "Malaquias": 39, "Mal": 39,
    "Mateo": 40, "Mt": 40, "Mat": 40,
    "Marcos": 41, "Mr": 41, "Mc": 41,
    "Lucas": 42, "Lc": 42, "Luc": 42,
    "Juan": 43, "Jn": 43,
    "Hechos": 44, "Hch": 44,
    "Romanos": 45, "Rom": 45, "Ro": 45,
    "1 Corintios": 46, "1 Co": 46, "1Co": 46, "1 Cor": 46,
    "2 Corintios": 47, "2 Co": 47, "2Co": 47, "2 Cor": 47,
    "Gálatas": 48, "Galatas": 48, "Gal": 48, "Ga": 48,
    "Efesios": 49, "Efe": 49, "Ef": 49,
    "Filipenses": 50, "Fil": 50, "Flp": 50,
    "Colosenses": 51, "Col": 51,
    "1 Tesalonicenses": 52, "1 Ts": 52, "1Ts": 52, "1 Tes": 52,
    "2 Tesalonicenses": 53, "2 Ts": 53, "2Ts": 53, "2 Tes": 53,
    "1 Timoteo": 54, "1 Ti": 54, "1Ti": 54, "1 Tim": 54,
    "2 Timoteo": 55, "2 Ti": 55, "2Ti": 55, "2 Tim": 55,
    "Tito": 56, "Tit": 56,
    "Filemón": 57, "Filemon": 57, "Flm": 57,
    "Hebreos": 58, "Heb": 58,
    "Santiago": 59, "Stg": 59, "St": 59,
    "1 Pedro": 60, "1 Pe": 60, "1Pe": 60, "1 P": 60,
    "2 Pedro": 61, "2 Pe": 61, "2Pe": 61, "2 P": 61,
    "1 Juan": 62, "1 Jn": 62, "1Jn": 62,
    "2 Juan": 63, "2 Jn": 63, "2Jn": 63,
    "3 Juan": 64, "3 Jn": 64, "3Jn": 64,
    "Judas": 65, "Jud": 65,
    "Apocalipsis": 66, "Ap": 66, "Apo": 66,
}

_canonical_names = {}
for name, bid in LIBROS_BIBLICOS.items():
    if bid not in _canonical_names:
        _canonical_names[bid] = name

def _book_id_to_slug(book_id: int) -> str:
    """Convierte ID de libro a nombre URL-friendly (ej: 58 -> hebreos)."""
    name = _canonical_names.get(book_id, "")
    name = name.lower()
    name = name.replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("á", "a")
    return name

_books_pattern = "|".join(sorted(LIBROS_BIBLICOS.keys(), key=len, reverse=True))
# Pattern: optional number prefix + book name + chapter:verse(optional -verse_end)
_REF_PATTERN = re.compile(
    rf"(?:^|\s|[(\[{{>])(\d+\s+)?({_books_pattern})\s+(\d+):(\d+)(?:\s*[-–]\s*(\d+))?(?=\s|[)\].,;:!?<]|$)",
    re.IGNORECASE,
)

def normalizar_libro(nombre: str) -> str:
    """Normaliza nombre de libro para lookup."""
    n = nombre.strip()
    for key in LIBROS_BIBLICOS:
        if key.lower() == n.lower():
            return key
    return n

def parse_referencia(texto: str) -> List[Dict]:
    """Parsea todas las referencias bíblicas en un texto."""
    referencias = []
    for match in _REF_PATTERN.finditer(texto):
        num_prefix = match.group(1)
        raw_name = match.group(2)
        chapter = int(match.group(3))
        verse_start = int(match.group(4))
        verse_end = int(match.group(5)) if match.group(5) else None

        full_name = raw_name
        if num_prefix:
            full_name = f"{num_prefix.strip()} {raw_name}"

        book_id = LIBROS_BIBLICOS.get(full_name) or LIBROS_BIBLICOS.get(raw_name)
        if not book_id:
            continue

        ref_text = match.group(0).strip()
        start_pos = match.start()
        end_pos = match.end()

        referencias.append({
            "book_id": book_id,
            "book_name": raw_name,
            "chapter": chapter,
            "verse_start": verse_start,
            "verse_end": verse_end,
            "reference": ref_text.strip("()[]{} "),
            "start_pos": start_pos,
            "end_pos": end_pos,
        })
    return referencias


def _md_a_href(match):
    """Replacement function: wraps bible reference match in an anchor tag."""
    prefix = match.group(0)[0] if match.group(0) and match.group(0)[0] in " \t\n\r([{<>" else ""
    book_name = match.group(2)
    num_prefix = match.group(1)
    chapter = match.group(3)
    verse_start = match.group(4)
    verse_end = match.group(5)

    full_name = book_name
    if num_prefix:
        full_name = f"{num_prefix.strip()} {book_name}"

    book_id = LIBROS_BIBLICOS.get(full_name) or LIBROS_BIBLICOS.get(book_name)
    ref_text = match.group(0).strip().strip("()[]{} <>")

    if book_id:
        slug = _book_id_to_slug(book_id)
        return f'{prefix}<a href="/{slug}/{chapter}/{verse_start}" class="bible-ref" data-book="{book_id}" data-chapter="{chapter}" data-verse="{verse_start}">{ref_text}</a>'
    return match.group(0)

def marcar_referencias_html(texto: str, base_url: str = "") -> str:
    """Convierte markdown a HTML con referencias bíblicas enlazadas."""
    md_html = markdown.markdown(texto, extensions=["extra", "codehilite"])
    html = _REF_PATTERN.sub(_md_a_href, md_html)
    return html


def extraer_tags_automaticos(content: str) -> List[str]:
    """Extrae tags relevantes del contenido basado en palabras clave."""
    keywords = {
        "discipulado": ["discípulo", "discipulado", "discipulos", "madurez"],
        "oracion": ["oración", "oracion", "orar", "orando"],
        "santidad": ["santo", "santidad", "santificación", "santificacion", "santificar"],
        "espiritu-santo": ["espíritu santo", "espiritu santo", "espíritu", "espiritu"],
        "fe": ["fe", "creer", "confianza"],
        "gracia": ["gracia", "gratitud"],
        "amor": ["amor", "amar", "ágape", "agape"],
        "salvacion": ["salvación", "salvacion", "redencion", "redención", "nuevo nacimiento"],
        "iglesia": ["iglesia", "congregación", "congregacion", "cuerpo de cristo"],
        "ayuno": ["ayuno", "ayunar"],
        "diezmos": ["diezmo", "diezmos", "ofrenda", "ofrendas", "mayordomía", "mayordomia", "generosidad"],
        "escrituras": ["escritura", "biblia", "palabra de dios", "las escrituras"],
        "profecia": ["profecía", "profecia", "profético", "profetico", "apocalipsis"],
        "sabiduria": ["sabiduría", "sabiduria", "proverbios", "eclesiastés", "eclesiastes"],
        "jesus": ["jesús", "jesus", "cristo", "señor", "mesías", "mesias"],
        "paz": ["paz", "gozo", "paciencia"],
        "perdon": ["perdón", "perdon", "perdonar"],
        "servicio": ["servicio", "servir", "ministerio", "don", "dones"],
        "esperanza": ["esperanza", "eterna", "eternidad"],
    }
    content_lower = content.lower()
    encontradas = []
    for tag, palabras in keywords.items():
        for p in palabras:
            if p in content_lower:
                encontradas.append(tag)
                break
    return encontradas
