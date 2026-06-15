import io
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.app.run import create_app


@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config.update(TESTING=True)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_analyze_requires_auth_and_returns_json(client):
    response = client.post("/analyze", data={})

    assert response.status_code == 401
    assert response.is_json
    body = response.get_json()
    assert body["error"] == "Authentication required"


def test_analyze_validation_error_is_json_for_authenticated_user(client):
    with client.session_transaction() as sess:
        sess["logged_in"] = True
        sess["user_id"] = 999999

    data = {
        "file": (io.BytesIO(b""), "empty.json"),
        "confidence": "0.95",
    }
    response = client.post("/analyze", data=data, content_type="multipart/form-data")

    assert response.status_code == 400
    assert response.is_json
    body = response.get_json()
    assert "error" in body
