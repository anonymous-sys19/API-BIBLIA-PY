"""Backfill miniatura_url para registros existentes sin miniatura."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
import libsql

load_dotenv()

DB_URL = os.getenv("TURSO_DB_URL", "")
AUTH_TOKEN = os.getenv("TURSO_AUTH_TOKEN", "")

if not DB_URL or not AUTH_TOKEN:
    print("ERROR: TURSO_DB_URL y TURSO_AUTH_TOKEN deben estar en .env")
    sys.exit(1)


def main():
    conn = libsql.connect(DB_URL, auth_token=AUTH_TOKEN) # type: ignore

    result = conn.execute(
        "SELECT id, video_id, tipo, miniatura_url FROM videos WHERE miniatura_url IS NULL OR miniatura_url = ''"
    )
    rows = result.fetchall()
    columns = [desc[0] for desc in result.description]

    if not rows:
        print("✓ No hay videos sin miniatura")
        return

    updated = 0
    for row in rows:
        data = {col: val for col, val in zip(columns, row)}
        vid = data["video_id"]
        tipo = data["tipo"] or "youtube"

        if tipo in ("youtube", "video"):
            new_url = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
        elif tipo == "spotify":
            new_url = f"https://i.scdn.co/image/ab67616d0000b273{vid[:20]}" if len(vid) > 10 else None
        else:
            continue

        if not new_url:
            continue

        conn.execute("UPDATE videos SET miniatura_url = ? WHERE id = ?", [new_url, data["id"]])
        print(f"  ✓ {data['id']:>4} | {tipo:8} | {vid:<15} → miniatura asignada")
        updated += 1

    conn.commit()
    print(f"\n✓ {updated} miniaturas actualizadas y guardadas")
    conn.close()


if __name__ == "__main__":
    main()
