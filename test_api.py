#!/usr/bin/env python3
"""
Script de prueba rápida de la API Bíblica
Verifica conectividad a BD y endpoints básicos
"""

import sqlite3
import sys
from pathlib import Path

# Agregar el proyecto al path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.db.database import Biblia


def test_database_connection():
    """Prueba conexión a la base de datos"""
    print("🔍 Probando conexión a base de datos...")
    try:
        biblia = Biblia("rvr1960.sqlite")
        stats = biblia.obtener_estadisticas()
        print(f"   ✅ BD conectada")
        print(f"   📊 Estadísticas: {stats}")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_obtener_libros():
    """Prueba obtener libros"""
    print("\n📚 Probando obtener_libros()...")
    try:
        biblia = Biblia("rvr1960.sqlite")
        libros = biblia.obtener_libros()
        print(f"   ✅ Obtenidos {len(libros)} libros")
        if libros:
            print(f"   Primer libro: {libros[0].name} ({libros[0].abbreviation})")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_obtener_libro_por_abreviacion():
    """Prueba buscar libro por abreviación"""
    print("\n📖 Probando obtener_libro_por_abreviacion()...")
    try:
        biblia = Biblia("rvr1960.sqlite")
        libro = biblia.obtener_libro_por_abreviacion("Jn")
        if libro:
            print(f"   ✅ Libro encontrado: {libro.name} ({libro.chapters} capítulos)")
        else:
            print("   ⚠️  Libro no encontrado")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_obtener_verso():
    """Prueba obtener un versículo (Juan 3:16)"""
    print("\n✝️  Probando obtener_verso()...")
    try:
        biblia = Biblia("rvr1960.sqlite")
        verso = biblia.obtener_verso(book_id=43, chapter=3, verse=16)  # John 3:16
        if verso:
            print(f"   ✅ Versículo encontrado: {verso.book_name} {verso.chapter}:{verso.verse}")
            print(f"   Texto: {verso.text[:80]}...")
        else:
            print("   ⚠️  Versículo no encontrado")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_obtener_capitulo():
    """Prueba obtener un capítulo"""
    print("\n📕 Probando obtener_capitulo()...")
    try:
        biblia = Biblia("rvr1960.sqlite")
        versos = biblia.obtener_capitulo(book_id=43, chapter=1)  # John 1
        if versos:
            print(f"   ✅ Capítulo encontrado con {len(versos)} versículos")
        else:
            print("   ⚠️  Capítulo no encontrado")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def test_buscar_en_versos():
    """Prueba búsqueda"""
    print("\n🔎 Probando buscar_en_versos()...")
    try:
        biblia = Biblia("rvr1960.sqlite")
        resultados = biblia.buscar_en_versos("amor", limit=5)
        if resultados:
            print(f"   ✅ Búsqueda exitosa: {len(resultados)} resultados")
            print(f"   Primer resultado: {resultados[0].book_name} {resultados[0].chapter}:{resultados[0].verse}")
        else:
            print("   ⚠️  Sin resultados")
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Ejecuta todas las pruebas"""
    print("=" * 60)
    print("🧪 PRUEBAS DE API-BIBLIA-PY")
    print("=" * 60)
    
    tests = [
        test_database_connection,
        test_obtener_libros,
        test_obtener_libro_por_abreviacion,
        test_obtener_verso,
        test_obtener_capitulo,
        test_buscar_en_versos,
    ]
    
    results = [test() for test in tests]
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMEN: {sum(results)}/{len(results)} pruebas exitosas")
    print("=" * 60)
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
