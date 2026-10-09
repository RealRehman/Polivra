
from fastapi.testclient import TestClient

from app.main import app

from types import SimpleNamespace
from uuid import uuid4

import app.routes.documents as document_routes
from app.security.dependencies import get_current_user

from app.schemas.document import DocumentResponse


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_auth_me_requires_authentication():
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_list_documents_requires_authentication():
    response = client.get("/documents")

    assert response.status_code == 401


def test_get_organization_details_requires_authentication():
    response = client.get("/organizations/me")

    assert response.status_code == 401
    

def test_archived_document_detail_returns_404(monkeypatch):
    document_id = uuid4()

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=uuid4(),
        organization_id=uuid4(),
    )

    monkeypatch.setattr(
        document_routes,
        "get_organization_document",
        lambda db, document_id, organization_id: None,
    )

    try:
        response = client.get(f"/documents/{document_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Document not found"
    finally:
        app.dependency_overrides.pop(get_current_user, None)


def test_document_response_does_not_expose_file_key():
    assert "file_key" not in DocumentResponse.model_fields


def test_document_list_uses_authenticated_organization(monkeypatch):
    organization_id = uuid4()

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(
        id=uuid4(),
        organization_id=organization_id,
    )

    captured = {}

    def fake_get_documents(db, requested_organization_id):
        captured["organization_id"] = requested_organization_id
        return []

    monkeypatch.setattr(
        document_routes,
        "get_organization_documents",
        fake_get_documents,
    )

    try:
        response = client.get("/documents")

        assert response.status_code == 200
        assert response.json() == []
        assert captured["organization_id"] == organization_id
    finally:
        app.dependency_overrides.pop(get_current_user, None)
