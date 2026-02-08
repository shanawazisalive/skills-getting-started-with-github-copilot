import pytest
from fastapi.testclient import TestClient


def test_get_activities(client):
    """Test retrieving all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "Basketball" in data
    assert "Tennis" in data
    assert "Art Club" in data
    
    # Check Basketball activity structure
    basketball = data["Basketball"]
    assert "description" in basketball
    assert "schedule" in basketball
    assert "max_participants" in basketball
    assert "participants" in basketball
    assert isinstance(basketball["participants"], list)


def test_signup_for_activity_success(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Basketball/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert "newstudent@mergington.edu" in data["message"]


def test_signup_duplicate_participant(client):
    """Test that a student cannot sign up twice for the same activity"""
    # First signup
    response1 = client.post(
        "/activities/Basketball/signup",
        params={"email": "alex@mergington.edu"}
    )
    assert response1.status_code == 400
    
    data = response1.json()
    assert "already signed up" in data["detail"].lower()


def test_signup_nonexistent_activity(client):
    """Test signup for an activity that doesn't exist"""
    response = client.post(
        "/activities/NonexistentActivity/signup",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_unregister_success(client):
    """Test successful unregistration from an activity"""
    response = client.delete(
        "/activities/Basketball/unregister",
        params={"email": "alex@mergington.edu"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]


def test_unregister_nonexistent_participant(client):
    """Test unregistering a student who isn't signed up"""
    response = client.delete(
        "/activities/Basketball/unregister",
        params={"email": "notstudent@mergington.edu"}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "not signed up" in data["detail"].lower()


def test_unregister_nonexistent_activity(client):
    """Test unregistering from an activity that doesn't exist"""
    response = client.delete(
        "/activities/NonexistentActivity/unregister",
        params={"email": "student@mergington.edu"}
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


def test_signup_then_unregister_workflow(client):
    """Test complete workflow: signup and then unregister"""
    email = "workflow@mergington.edu"
    activity = "Tennis"
    
    # Sign up
    signup_response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    assert signup_response.status_code == 200
    
    # Verify signup in activities
    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity]["participants"]
    
    # Unregister
    unregister_response = client.delete(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert unregister_response.status_code == 200
    
    # Verify unregister in activities
    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity]["participants"]


def test_multiple_participants_same_activity(client):
    """Test adding multiple participants to the same activity"""
    activity = "Art Club"
    emails = [
        "student1@mergington.edu",
        "student2@mergington.edu",
        "student3@mergington.edu"
    ]
    
    # Sign up all students
    for email in emails:
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify all are signed up
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity]["participants"]
    
    for email in emails:
        assert email in participants


def test_root_redirect(client):
    """Test that root redirects to static index"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"
