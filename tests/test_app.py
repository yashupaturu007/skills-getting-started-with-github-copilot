"""
API tests for Mergington High School Activities FastAPI application.
Tests follow the Arrange-Act-Assert (AAA) pattern for clarity and maintainability.
"""

import pytest
from fastapi.testclient import TestClient
from src import app as app_module


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static(self, client: TestClient):
        """
        Arrange: Prepare test client
        Act: Make GET request to /
        Assert: Verify redirect to /static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all(self, client: TestClient):
        """
        Arrange: Fresh activities fixture is auto-applied
        Act: Make GET request to /activities
        Assert: Verify all activities are returned with correct data
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data

    def test_get_activities_has_required_fields(self, client: TestClient):
        """
        Arrange: Fresh activities fixture is auto-applied
        Act: Make GET request to /activities
        Assert: Verify each activity has required fields
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client: TestClient):
        """
        Arrange: Fresh activities with known state
        Act: Sign up a new participant to an available activity
        Assert: Verify 200 status, success message, and participant added
        """
        # Arrange
        activity_name = "Gym Class"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Signed up {email} for {activity_name}"
        assert email in app_module.activities[activity_name]["participants"]

    def test_signup_duplicate_rejected(self, client: TestClient):
        """
        Arrange: Fresh activities with michael@mergington.edu in Chess Club
        Act: Try to sign up the same email again
        Assert: Verify 400 status and error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student already signed up for this activity"

    def test_signup_invalid_activity(self, client: TestClient):
        """
        Arrange: Fresh activities fixture
        Act: Try to sign up for non-existent activity
        Assert: Verify 404 status and error message
        """
        # Arrange
        activity_name = "NonExistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"


class TestRemoveEndpoint:
    """Tests for DELETE /activities/{activity_name}/remove endpoint."""

    def test_remove_success(self, client: TestClient):
        """
        Arrange: Fresh activities with michael@mergington.edu in Chess Club
        Act: Remove the participant from the activity
        Assert: Verify 200 status, message, and participant removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        assert email in app_module.activities[activity_name]["participants"]
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == f"Removed {email} from {activity_name}"
        assert email not in app_module.activities[activity_name]["participants"]

    def test_remove_not_registered(self, client: TestClient):
        """
        Arrange: Fresh activities with unregistered student
        Act: Try to remove participant not signed up
        Assert: Verify 400 status and error message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notstudent@mergington.edu"  # Not signed up
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert data["detail"] == "Student is not signed up for this activity"

    def test_remove_invalid_activity(self, client: TestClient):
        """
        Arrange: Fresh activities fixture
        Act: Try to remove from non-existent activity
        Assert: Verify 404 status and error message
        """
        # Arrange
        activity_name = "NonExistent Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/remove",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Activity not found"
