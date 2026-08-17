"""
Pytest configuration and fixtures for FastAPI application tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app as fastapi_app
from src import app as app_module


@pytest.fixture
def app():
    """Fixture that provides the FastAPI app instance."""
    return fastapi_app


@pytest.fixture
def client(app):
    """Fixture that provides a test client for making requests."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def fresh_activities():
    """
    Fixture that resets activities to a known state before each test.
    Ensures test isolation by preventing tests from affecting each other.
    """
    # Save original activities
    original_activities = app_module.activities.copy()
    
    # Reset activities to a fresh state for testing
    app_module.activities.clear()
    app_module.activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": []
        }
    })
    
    # Yield control to the test
    yield
    
    # Restore original activities after test completes
    app_module.activities.clear()
    app_module.activities.update(original_activities)
