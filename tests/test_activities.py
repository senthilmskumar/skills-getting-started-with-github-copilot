import copy
import json

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture(autouse=True)
def reset_activities():
    # Snapshot and restore activities to keep tests isolated
    original = json.loads(json.dumps(app_module.activities))
    yield
    # Deep-restore
    app_module.activities = copy.deepcopy(original)


def test_signup_and_unregister_flow():
    client = TestClient(app_module.app)

    # initial participants
    before = client.get("/activities").json()["Chess Club"]["participants"]

    # signup with valid domain
    r = client.post("/activities/Chess%20Club/signup?email=testuser@mergington.edu")
    assert r.status_code == 200
    assert "Signed up" in r.json()["message"]

    after = client.get("/activities").json()["Chess Club"]["participants"]
    assert "testuser@mergington.edu" in after

    # unregister
    r = client.delete("/activities/Chess%20Club/unregister?email=testuser@mergington.edu")
    assert r.status_code == 200
    assert "Unregistered" in r.json()["message"]

    final = client.get("/activities").json()["Chess Club"]["participants"]
    assert "testuser@mergington.edu" not in final


def test_signup_rejects_wrong_domain():
    client = TestClient(app_module.app)
    r = client.post("/activities/Chess%20Club/signup?email=baduser@example.com")
    assert r.status_code == 400
    assert r.json().get("detail") == "Email must be a mergington.edu address"


def test_unregister_rejects_wrong_domain():
    client = TestClient(app_module.app)
    r = client.delete("/activities/Chess%20Club/unregister?email=baduser@example.com")
    assert r.status_code == 400
    assert r.json().get("detail") == "Email must be a mergington.edu address"
