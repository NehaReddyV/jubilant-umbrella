from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Reset the in-memory activities to a known state before each test
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
        },
    })
    yield


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]


def test_signup_for_activity():
    email = "newstudent@example.com"
    activity_name = "Chess Club"
    # ensure not already signed up
    assert email not in activities[activity_name]["participants"]

    url = f"/activities/{quote(activity_name)}/signup"
    resp = client.post(url, params={"email": email})
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body["message"]

    # verify participant was added
    resp2 = client.get("/activities")
    data = resp2.json()
    assert email in data[activity_name]["participants"]


def test_unregister_participant():
    activity_name = "Chess Club"
    email = "toremove@example.com"

    # add participant first
    activities[activity_name]["participants"].append(email)
    assert email in activities[activity_name]["participants"]

    url = f"/activities/{quote(activity_name)}/participants"
    resp = client.delete(url, params={"email": email})
    assert resp.status_code == 200
    body = resp.json()
    assert "Unregistered" in body["message"]

    # verify removed
    resp2 = client.get("/activities")
    data = resp2.json()
    assert email not in data[activity_name]["participants"]
