"""HTTP transport tests using a canned Lyria-shaped manifest store."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mtl_c2pa_server import c2pa as c2pa_mod
from mtl_c2pa_server.http import app


LYRIA_STORE = {
    "active_manifest": "urn:c2pa:80faaddf-fe27-1e7d-0ce5-4a70eeba2dd1",
    "manifests": {
        "urn:c2pa:80faaddf-fe27-1e7d-0ce5-4a70eeba2dd1": {
            "claim_generator_info": [
                {
                    "name": "Google C2PA Core Generator Library",
                    "version": "916434528:916944653",
                }
            ],
            "instance_id": "347d89b0-7e42-e884-20f6-44cf622e4ff8",
            "assertions": [
                {
                    "label": "c2pa.actions.v2",
                    "data": {
                        "actions": [
                            {
                                "action": "c2pa.created",
                                "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
                                "description": "Created by Google Generative AI.",
                            },
                            {
                                "action": "c2pa.edited",
                                "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
                                "description": "Applied imperceptible SynthID watermark.",
                            },
                        ]
                    },
                }
            ],
            "ingredients": [],
            "signature_info": {"issuer": "Google LLC"},
        }
    },
    "validation_state": "valid",
}


@pytest.fixture
def fake_mp3(tmp_path: Path) -> Path:
    p = tmp_path / "Sovereign_Ascent.mp3"
    p.write_bytes(b"\xff\xfb\x90\x00")
    return p


@pytest.fixture(autouse=True)
def stub_read_manifest_store(monkeypatch, fake_mp3):
    def _fake(file_path: str):
        path = c2pa_mod._resolve_path(file_path)
        c2pa_mod._mime_for(path)
        return LYRIA_STORE

    monkeypatch.setattr(c2pa_mod, "read_manifest_store", _fake)


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_summary_endpoint_flags_ai(client, fake_mp3):
    resp = client.post("/summary", json={"path": str(fake_mp3)})
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_ai_generated"] is True
    assert data["signature_issuer"] == "Google LLC"


def test_summary_endpoint_extracts_actions(client, fake_mp3):
    resp = client.post("/summary", json={"path": str(fake_mp3)})
    data = resp.json()
    actions = [a["action"] for a in data["actions"]]
    assert actions == ["c2pa.created", "c2pa.edited"]


def test_summary_detects_synthid_watermark(client, fake_mp3):
    resp = client.post("/summary", json={"path": str(fake_mp3)})
    descriptions = [w.get("description", "") for w in resp.json()["watermarks"]]
    assert any("SynthID" in d for d in descriptions)


def test_read_endpoint_returns_store(client, fake_mp3):
    resp = client.post("/read", json={"path": str(fake_mp3)})
    assert resp.status_code == 200
    assert resp.json()["active_manifest"].startswith("urn:c2pa:")


def test_assertions_endpoint(client, fake_mp3):
    resp = client.post("/assertions", json={"path": str(fake_mp3)})
    assert resp.status_code == 200
    assert resp.json()["assertions"][0]["label"] == "c2pa.actions.v2"


def test_ingredients_endpoint_empty_for_ai_track(client, fake_mp3):
    resp = client.post("/ingredients", json={"path": str(fake_mp3)})
    assert resp.status_code == 200
    assert resp.json()["ingredients"] == []


def test_verify_endpoint_reports_valid(client, fake_mp3):
    resp = client.post("/verify", json={"path": str(fake_mp3)})
    assert resp.status_code == 200
    data = resp.json()
    assert data["is_valid"] is True
    assert data["signature_issuer"] == "Google LLC"
    assert data["failures"] == []


def test_info_endpoint(client):
    resp = client.get("/info")
    assert resp.status_code == 200
    data = resp.json()
    assert data["available"] is True
    assert "audio/mpeg" in data["supported_mime_types"]


def test_health_endpoint(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_missing_file_returns_404(client, tmp_path):
    resp = client.post("/summary", json={"path": str(tmp_path / "nope.mp3")})
    assert resp.status_code == 404
    body = resp.json()
    assert "error" in body
    assert body["error_type"] == "FileNotFoundError"


def test_unsupported_extension_returns_400(client, tmp_path):
    junk = tmp_path / "weird.xyz"
    junk.write_bytes(b"")
    resp = client.post("/summary", json={"path": str(junk)})
    assert resp.status_code == 400
    body = resp.json()
    assert body["error_type"] == "ValueError"


def test_invalid_payload_returns_422(client):
    resp = client.post("/summary", json={})
    assert resp.status_code == 422
