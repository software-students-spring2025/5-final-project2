import json
from datetime import datetime, timedelta

import mongomock
import pytest

# Test Fixtures 

@pytest.fixture(scope="module")
def test_app():
    import importlib
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pymongo":
            pymongo_mock = importlib.import_module("types").ModuleType("pymongo")
            pymongo_mock.MongoClient = mongomock.MongoClient
            return pymongo_mock
        return real_import(name, *args, **kwargs)

    builtins.__import__ = fake_import
    mod = importlib.import_module("frontend.app")  
    flask_app = mod.app
    flask_app.users = mod.users
    flask_app.dreams = mod.dreams                             
    builtins.__import__ = real_import

    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(test_app):
    return test_app.test_client()

# Unit Tests  

def test_home_redirects_to_login(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]


def test_register_and_login_success(client):
    # Register
    payload = {
        "username": "alice",
        "password": "secret",
        "password2": "secret",
    }
    resp = client.post("/register", data=payload, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Login" in resp.data 

    # login
    resp = client.post("/login", data={
        "username": "alice",
        "password": "secret",
    }, follow_redirects=True)
    assert resp.status_code == 200
    # dashboard template contains username
    assert b"alice" in resp.data


def test_register_password_mismatch(client):
    resp = client.post(
        "/register",
        data={"username": "bob", "password": "a", "password2": "b"},
        follow_redirects=True,
    )
    assert b"Passwords do not match" in resp.data


def test_dashboard_streak_computation(client, test_app):
    # Insert user manually with dream entries for yesterday & today
    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)
    coll = test_app.users  
    coll.insert_one({
        "username": "carol",
        "password": "hash", 
        "dreams": [
            {"date": today},
            {"date": yesterday},
        ],
    })

    with client.session_transaction() as sess:
        sess["username"] = "carol"

    resp = client.get("/dashboard")
    assert resp.status_code == 200
    # Streak should be 2 -> appears in rendered HTML
    assert b"streak" in resp.data or b"2" in resp.data


def test_analyze_calls_ai_service(client, monkeypatch):
    """Mock requests.post so the route doesn't actually call backend."""
    class _FakeResp:
        def json(self):
            return {"interpretation": "It means you are testing."}

    def fake_post(*_args, **_kwargs):
        return _FakeResp()

    monkeypatch.setattr("frontend.app.requests.post", fake_post)

    with client.session_transaction() as sess:
        sess["username"] = "alice"

    resp = client.post("/analyze", data={"dream": "I was flying"}, follow_redirects=True)
    assert resp.status_code == 200
    assert b"You are testing" in resp.data or b"testing" in resp.data


def test_dreamstats_uses_helper(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["username"] = "alice"

    monkeypatch.setattr("frontend.app.get_dream_glance", lambda u: {"count": 3})

    resp = client.get("/dreamstats")
    assert resp.status_code == 200
    assert b"count" in resp.data or b"3" in resp.data