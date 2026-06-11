#!/usr/bin/env python3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.main import app

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
