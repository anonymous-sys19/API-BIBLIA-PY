#!/usr/bin/env python3
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app
from app.db.models import GuiaEstudio
from fastapi.testclient import TestClient

client = TestClient(app)

def benchmark_endpoint(name, method, url, iterations=10):
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        if method == "GET":
            resp = client.get(url)
        elif method == "POST":
            resp = client.post(url[0], json=url[1])
        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)
    avg = sum(times) / len(times)
    p95 = sorted(times)[int(len(times) * 0.95)]
    print(f"{name:40s} avg={avg:6.1f}ms  p95={p95:6.1f}ms  status={resp.status_code}") # type: ignore
    return avg, p95

print("=" * 80)
print("BENCHMARK DE RENDIMIENTO - GhostRoot Bible API")
print("=" * 80)

payload = GuiaEstudio(
    id=None, title="Benchmark Guía", author="Test",
    content="Juan 3:16 y Romanos 8:28 y Efesios 2:8-9 y Gálatas 4:19 y Hebreos 11:1",
    tags="fe, gracia", status="published"
)
resp = client.post("/guide/add", json=payload.__dict__)
guia_id = resp.json()["id"]

print(f"\nGuía creada con ID: {guia_id}")
print(f"Contenido: 5 referencias bíblicas\n")

benchmark_endpoint("GET /guide (list paginado)", "GET", "/guide")
benchmark_endpoint("GET /guide?tag=fe (filtro tag)", "GET", "/guide?tag=fe")
benchmark_endpoint("GET /guide/tags", "GET", "/guide/tags")
benchmark_endpoint("GET /guide/{id} (sin HTML)", "GET", f"/guide/{guia_id}")
benchmark_endpoint("GET /guide/{id}?html=true", "GET", f"/guide/{guia_id}?html=true")
benchmark_endpoint("GET /guide/{id}/verses (batch)", "GET", f"/guide/{guia_id}/verses")
benchmark_endpoint("GET /juan/3/16 (verso simple)", "GET", "/juan/3/16")
benchmark_endpoint("GET /health", "GET", "/health")

print("\n" + "=" * 80)
print("OPTIMIZACIONES APLICADAS:")
print("=" * 80)
print("✓ content_html pre-computado y cacheado en DB")
print("✓ Paginación en listados (default: 20 items)")
print("✓ Batch lookup de versículos (sin N+1 queries)")
print("✓ Compresión GZip (min 500 bytes)")
print("✓ Rate limiting (120 req/min por IP)")
print("✓ Índices en DB (status, created_at, tags)")
print("✓ ETag headers para caché del cliente")
print("✓ Regex compilado una sola vez al importar")
print("=" * 80)

client.delete(f"/guide/{guia_id}")
