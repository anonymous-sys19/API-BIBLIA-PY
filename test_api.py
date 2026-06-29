#!/usr/bin/env python3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app
from app.db.models import GuiaEstudio

client = TestClient(app)


class TestHealth:
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestDocs:
    def test_home_returns_documentation_html(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "GhostRoot Bible API" in response.text
        assert "Introducción" in response.text

    def test_api_info_returns_json(self):
        response = client.get("/api-info")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert data["api"] == "GhostRoot Bible API"
        assert "endpoints" in data
        assert "versiones_disponibles" in data


class TestDaily:
    def test_daily_default_version(self):
        response = client.get("/daily")
        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert "book_name" in data
        assert "chapter" in data
        assert "verse" in data

    def test_daily_with_version(self):
        response = client.get("/daily/rvr1960")
        assert response.status_code == 200
        data = response.json()
        assert "text" in data


class TestList:
    def test_list_testaments(self):
        response = client.get("/list/testaments")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_list_books(self):
        response = client.get("/list/books")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_list_books_filter_antiguo(self):
        response = client.get("/list/books/antiguo")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for book in data:
            assert book["testament_id"] == 1

    def test_list_books_filter_nuevo(self):
        response = client.get("/list/books/nuevo")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for book in data:
            assert book["testament_id"] == 2


class TestInfo:
    def test_chapters_count(self):
        response = client.get("/info/chapters/1")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert data["total"] > 0

    def test_verses_count(self):
        response = client.get("/info/verses/1/1")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert data["total"] > 0


class TestChapters:
    def test_get_chapter_by_name(self):
        response = client.get("/genesis/1")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_chapter_by_id(self):
        response = client.get("/bible/1/1")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_chapter_invalid_book(self):
        response = client.get("/libroinexistente/1")
        assert response.status_code == 404


class TestVerses:
    def test_get_verse_by_name(self):
        response = client.get("/juan/3/16")
        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert data["chapter"] == 3
        assert data["verse"] == 16

    def test_get_verse_not_found(self):
        response = client.get("/juan/999/999")
        assert response.status_code == 404


class TestSearch:
    def test_search_basic(self):
        response = client.get("/search/amor")
        assert response.status_code == 200
        data = response.json()
        assert "busqueda" in data
        assert "cantidad" in data
        assert "resultados" in data

    def test_search_with_accents(self):
        response = client.get("/search/amó")
        assert response.status_code == 200
        data = response.json()
        assert data["cantidad"] >= 0

    def test_search_empty(self):
        response = client.get("/search/   ")
        assert response.status_code == 200
        data = response.json()
        assert data == []


class TestStream:
    def test_list_radios(self):
        response = client.get("/stream")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestVideos:
    def test_list_videos(self):
        response = client.get("/videos")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestAdminUI:
    def test_admin_ui_serves_html(self):
        response = client.get("/admin")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
        assert "GhostRoot Admin" in response.text


class TestSkillDownload:
    def test_download_skill_endpoint(self):
        response = client.get("/download/skill")
        assert response.status_code == 200
        assert "text/markdown" in response.headers["content-type"]
        assert "attachment" in response.headers["content-disposition"]
        assert "ghostroot-bible-api-skill.md" in response.headers["content-disposition"]


class TestGuia:
    def test_list_guias(self):
        response = client.get("/guide")
        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "pagination" in data
        assert isinstance(data["data"], list)

    def test_list_guias_pagination(self):
        response = client.get("/guide?page=1&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["limit"] == 5

    def test_get_guia_not_found(self):
        response = client.get("/guide/99999")
        assert response.status_code == 404

    def test_list_tags(self):
        response = client.get("/guide/tags")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_create_and_delete_guia(self):
        payload = GuiaEstudio(
            id=None, title="Test Guía de Prueba", author="",
            content="Porque de tal manera amó Dios al mundo que ha dado a su Hijo unigénito (Juan 3:16).",
            tags="test, fe", status="published"
        )
        response = client.post("/guide/add", json=payload.__dict__)
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        guia_id = data.get("id")
        assert guia_id is not None

        get_resp = client.get(f"/guide/{guia_id}")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["title"] == "Test Guía de Prueba"

        del_resp = client.delete(f"/guide/{guia_id}")
        assert del_resp.status_code == 200
        assert "mensaje" in del_resp.json()

    def test_create_guia_empty_tags(self):
        payload = GuiaEstudio(
            id=None, title="Guía Sin Tags", author="",
            content="La fe es la certeza de lo que se espera (Hebreos 11:1). La oración es el medio por el cual nos comunicamos con Dios (Filipenses 4:6-7).",
            tags="", status="published"
        )
        response = client.post("/guide/add", json=payload.__dict__)
        assert response.status_code == 200
        data = response.json()
        guia_id = data.get("id")
        assert guia_id is not None

        get_resp = client.get(f"/guide/{guia_id}")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert "tag_list" in get_data

    def test_update_guia(self):
        payload = GuiaEstudio(
            id=None, title="Guía a Actualizar", author="",
            content="Contenido inicial.",
            tags="", status="draft"
        )
        resp = client.post("/guide/add", json=payload.__dict__)
        guia_id = resp.json()["id"]

        update_payload = GuiaEstudio(
            id=None, title="Guía Actualizada", author="",
            content="Contenido inicial.",
            tags="fe, gracia", status="published"
        )
        update_resp = client.put(f"/guide/{guia_id}", json=update_payload.__dict__)
        assert update_resp.status_code == 200

        get_resp = client.get(f"/guide/{guia_id}")
        assert get_resp.status_code == 200
        get_data = get_resp.json()
        assert get_data["title"] == "Guía Actualizada"
        assert get_data["status"] == "published"

        client.delete(f"/guide/{guia_id}")

    def test_guia_verses(self):
        payload = GuiaEstudio(
            id=None, title="Guía con Versos", author="",
            content="Juan 3:16 y Romanos 8:28 y Gálatas 4:19",
            tags="", status="published"
        )
        resp = client.post("/guide/add", json=payload.__dict__)
        guia_id = resp.json()["id"]

        verses_resp = client.get(f"/guide/{guia_id}/verses")
        assert verses_resp.status_code == 200
        verses_data = verses_resp.json()
        assert len(verses_data) > 0
        assert "text" in verses_data[0]

        client.delete(f"/guide/{guia_id}")

    def test_guia_filter_by_tag(self):
        payload = GuiaEstudio(
            id=None, title="Guía para filtrar", author="",
            content="La oración es fundamental (Filipenses 4:6).",
            tags="oracion", status="published"
        )
        resp = client.post("/guide/add", json=payload.__dict__)
        guia_id = resp.json()["id"]

        filter_resp = client.get("/guide?tag=oracion")
        assert filter_resp.status_code == 200
        filter_data = filter_resp.json()
        titles = [g["title"] for g in filter_data["data"]]
        assert "Guía para filtrar" in titles

        client.delete(f"/guide/{guia_id}")

    def test_guia_html_content(self):
        payload = GuiaEstudio(
            id=None, title="Guía HTML", author="",
            content="Efesios 2:8-9 es un pasaje clave sobre la gracia.",
            tags="", status="published"
        )
        resp = client.post("/guide/add", json=payload.__dict__)
        guia_id = resp.json()["id"]

        html_resp = client.get(f"/guide/{guia_id}?html=true")
        assert html_resp.status_code == 200
        html_data = html_resp.json()
        assert "content_html" in html_data
        assert "bible-ref" in html_data["content_html"]

        client.delete(f"/guide/{guia_id}")

    def test_guia_404_on_delete(self):
        response = client.delete("/guide/99999")
        assert response.status_code == 404

    def test_guia_duplicate_creation(self):
        payload = GuiaEstudio(
            id=None, title="Test Duplicado", author="",
            content="Contenido de prueba.",
            tags="", status="published"
        )
        resp1 = client.post("/guide/add", json=payload.__dict__)
        assert resp1.status_code == 200
        id1 = resp1.json()["id"]

        resp2 = client.post("/guide/add", json=payload.__dict__)
        assert resp2.status_code == 200
        id2 = resp2.json()["id"]

        assert id2 != id1

        client.delete(f"/guide/{id1}")
        client.delete(f"/guide/{id2}")


class TestBrandAssets:
    def test_icon_svg_accessible(self):
        response = client.get("/static/img/icon.svg")
        assert response.status_code == 200
        assert "image/svg+xml" in response.headers["content-type"]

    def test_icon_jpg_accessible(self):
        response = client.get("/static/img/icon.jpg")
        assert response.status_code == 200
        assert "image/jpeg" in response.headers["content-type"]

    def test_api_info_includes_brand_assets(self):
        response = client.get("/api-info")
        assert response.status_code == 200
        data = response.json()
        assert "brand_assets" in data
        assert "icon_svg" in data["brand_assets"]
        assert "icon_jpg" in data["brand_assets"]
        assert data["brand_assets"]["icon_svg"] == "/static/img/icon.svg"
        assert data["brand_assets"]["icon_jpg"] == "/static/img/icon.jpg"
