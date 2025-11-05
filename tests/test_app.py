from fastapi.testclient import TestClient
from urllib.parse import quote
import src.app as app_module

client = TestClient(app_module.app)

ACTIVITY = "Chess Club"


def test_get_activities_structure():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert ACTIVITY in data
    participants = data[ACTIVITY]["participants"]
    # participants should be a list of objects with email/first_name/last_name
    assert isinstance(participants, list)
    if participants:
        p = participants[0]
        assert "email" in p
        assert "first_name" in p
        assert "last_name" in p


def test_signup_and_duplicate_and_invalid_domain_and_unregister():
    email = "teststudent@mergington.com"
    first_name = "Test"
    last_name = "Student"

    # Ensure the participant does not already exist (cleanup if needed)
    client.delete(f"/activities/{quote(ACTIVITY)}/participants", params={"email": email})

    # Successful signup
    resp = client.post(f"/activities/{quote(ACTIVITY)}/signup", params={
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
    })
    assert resp.status_code == 200
    assert first_name in resp.json().get("message", "")

    # Duplicate signup should fail
    resp_dup = client.post(f"/activities/{quote(ACTIVITY)}/signup", params={
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
    })
    assert resp_dup.status_code == 400

    # Invalid domain should be rejected
    resp_invalid = client.post(f"/activities/{quote(ACTIVITY)}/signup", params={
        "email": "baduser@example.com",
        "first_name": "Bad",
        "last_name": "User",
    })
    assert resp_invalid.status_code == 400

    # Unregister the test user
    resp_unreg = client.delete(f"/activities/{quote(ACTIVITY)}/participants", params={"email": email})
    assert resp_unreg.status_code == 200

    # Verify removal
    resp_after = client.get("/activities")
    participants = resp_after.json()[ACTIVITY]["participants"]
    emails = [p["email"] for p in participants]
    assert email not in [e.lower() for e in emails]