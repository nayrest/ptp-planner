import json
from fastapi.testclient import TestClient
from ptp.api import app

client = TestClient(app)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_gm_endpoint():
    data = load("examples/lesson2.json")
    data["t_max"] = 520
    r = client.post("/gm", json=data)
    assert r.status_code == 200
    body = r.json()
    assert body["gms"] == ["1", "2", "3"]
    assert sum(body["load"].values()) == 1100


def test_gm_no_backup_returns_400():
    data = load("examples/lesson2.json")
    data["t_max"] = 500
    r = client.post("/gm", json=data)
    assert r.status_code == 400


def test_rating_endpoint():
    data = load("examples/lesson3.json")
    data["budget"] = 50
    r = client.post("/rating", json=data)
    assert r.status_code == 200
    body = r.json()
    assert body["ranking"] == ["e1", "e2", "e3", "e5", "e4"]
    assert body["effect"] == 120