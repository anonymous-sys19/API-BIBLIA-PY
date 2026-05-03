import re
import unicodedata
from dataclasses import dataclass
from typing import List, Optional


def corregir_formato(texto: str) -> str:
    """
    Corrige caracteres rotos comunes en textos bíblicos (\\'f3, \\'e9, \\'ed, \\'fa, etc.)
    reemplazándolos por sus vocales acentuadas correspondientes.
    """
    # 1. Decodificar escapes hexadecimales como \'e1 (á), \'bf (¿), \'c9 (É)
    def decode_hex(match):
        try:
            return bytes.fromhex(match.group(1)).decode('cp1252')
        except:
            return match.group(0)
    
    # Buscamos el patrón \' seguido de dos caracteres hexadecimales
    texto = re.sub(r"\\\'([0-9a-fA-F]{2})", decode_hex, texto)
    
    # 2. Limpieza de etiquetas RTF complejas como {\i son} o \par{\qc\b\fs28 ...}
    # Eliminamos las llaves y comandos que empiezan con \
    texto = re.sub(r'\{|\}|\\[a-z]+-?\d*\s?', '', texto)
    
    return texto.strip()

def normalizar(texto: str) -> str:
    """Elimina tildes y convierte a minúsculas para comparaciones[cite: 1]."""
    texto = texto.lower()
    return "".join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def BIBLIAS_VERSIONES():
    return {
        "rvr1960": "app/files/rvr1960.sqlite",
        "nvi": "app/files/NVI1999.sqlite",
        "ntv": "app/files/ntv.sqlite",
        "pdt": "app/files/PDT8.sqlite",
        "bad": "app/files/bad.sqlite",
        "blsee": "app/files/BlSee.sqlite",
        "rvc": "app/files/RVC.sqlite",
        "rvg": "app/files/RVG10.sqlite",
    }
# DEFINIMOS CLASES DE LOS MODELOS DE LA API ---
@dataclass
class Verso:
    id: int
    book_id: int
    book_name: str
    chapter: int
    verse: int
    text: str
    version: str

    def __post_init__(self):
        self.text = corregir_formato(self.text)

@dataclass
class Libro:
    id: int
    name: str
    abbreviation: str
    chapters: int
    testament: str


@dataclass
class RadioStream:
    """Representa una emisora de radio en el sistema."""
    id: Optional[int]
    nombre: str
    url_stream: str
    pais: str = "Costa Rica"
    genero: str = "Cristiana"
    logo_url: Optional[str] = None
    status: str = "online"

@dataclass
class Video:
    """Representa un video de YouTube en el sistema."""
    id: Optional[int]
    video_id: str
    titulo: str
    canal_autor: Optional[str] = None
    tipo: Optional[str] = "video"
    miniatura_url: Optional[str] = None
    fecha_registro: Optional[str] = None