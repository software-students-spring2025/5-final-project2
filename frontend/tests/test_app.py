import importlib
import builtins
from datetime import datetime, timedelta

import mongomock
import pytest

@pytest.fixture(scope="module")
def test_app():
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pymongo":
            pymongo_mock = importlib.import_module("types").ModuleType("pymongo")
            pymongo_mock.MongoClient = mongomock.MongoClient
            return pymongo_mock
        return real_import(name, *args, **kwargs)

    builtins.__import__ = fake_import
    mod = importlib.import_module("frontend.app")
    builtins.__import__ = real_import

    flask_app = mod.app
    flask_app.config["TESTING"] = True
    flask_app.users = mod.users
    return flask_app

@pytest.fixture
def client(test_app):
    return test_app.test_client()



def test_home_redirects_to_login(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]

def test_register_and_login_success(client):
    resp = client.post("/register", data={
        "username": "alice", "password": "pw", "password2": "pw"
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Login" in resp.data

    resp = client.post("/login", data={
        "username": "alice", "password": "pw"
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"alice" in resp.data

def test_register_password_mismatch(client):
    resp = client.post("/register", data={
        "username": "bob", "password": "a", "password2": "b"
    }, follow_redirects=True)
    assert b"Passwords do not match" in resp.data

def test_logout_redirects_to_login(client):
    resp = client.get("/logout", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers["Location"]

def test_dashboard_streak_computation(client, test_app):
    coll = test_app.users
    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)
    coll.insert_one({
        "username": "carol",
        "password": "hash",
        "dreams": [
            {"date": today, "text": "x", "analysis": "y"},
            {"date": yesterday, "text": "a", "analysis": "b"},
        ],
    })
    with client.session_transaction() as sess:
        sess["username"] = "carol"

    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert b"2" in resp.data  

def test_analyze_empty_error(client):
    with client.session_transaction() as sess:
        sess["username"] = "dave"
    resp = client.post("/analyze", data={"dream": ""}, follow_redirects=True)
    assert b"Please enter a dream." in resp.data

def test_analyze_success_and_db_insert(client, test_app, monkeypatch):
    coll = test_app.users
    coll.insert_one({"username": "eve", "password": "pw", "dreams": []})

    class FakeResp:
        def json(self): return {"interpretation": "it works"}
    monkeypatch.setattr("frontend.app.requests.post", lambda *a, **k: FakeResp())

    with client.session_transaction() as sess:
        sess["username"] = "eve"
    resp = client.post("/analyze", data={"dream": "fly"}, follow_redirects=True)
    assert b"it works" in resp.data

def test_entries_requires_login(client):
    resp = client.get("/entries", follow_redirects=False)
    assert resp.status_code == 302 and "/login" in resp.headers["Location"]

def test_entries_shows_logged_dreams(client, test_app):
    coll = test_app.users
    coll.insert_one({
        "username": "frank", "password": "pw",
        "dreams": [{"date": datetime.utcnow(), "text": "hello", "analysis": "world"}]
    })
    with client.session_transaction() as sess:
        sess["username"] = "frank"

    resp = client.get("/entries")
    assert resp.status_code == 200
    assert b"hello" in resp.data and b"world" in resp.data

def test_dreamstats_success(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["username"] = "foo"
    fake = {"summary": "insights"}
    monkeypatch.setattr(
        "frontend.app.requests.get",
        lambda *a, **k: type("R", (), {"json": lambda self: fake})()
    )
    resp = client.get("/dreamstats")
    assert b"insights" in resp.data

def test_dreamstats_error(client, monkeypatch):
    with client.session_transaction() as sess:
        sess["username"] = "foo"
    monkeypatch.setattr("frontend.app.requests.get", lambda *a, **k: (_ for _ in ()).throw(Exception("fail")))
    resp = client.get("/dreamstats")
    assert b"Error fetching dream insights" in resp.data

def test_export_requires_login(client):
    resp = client.get("/export", follow_redirects=False)
    assert resp.status_code == 302 and "/login" in resp.headers["Location"]

def test_export_pdf_no_dreams(client, test_app):
    coll = test_app.users
    coll.insert_one({"username": "zoe", "password": "pw", "dreams": []})
    with client.session_transaction() as sess:
        sess["username"] = "zoe"
    resp = client.get("/export")
    assert resp.status_code == 200
    assert resp.headers["Content-Type"] == "application/pdf"
    assert resp.data.startswith(b"%PDF")