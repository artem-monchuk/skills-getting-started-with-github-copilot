"""Tests for GET /activities endpoint."""

import pytest
from fastapi.testclient import TestClient


class TestActivities:
    """Test suite for retrieving activities."""

    def test_get_all_activities_returns_success(self, client):
        """
        Arrange: TestClient ready with activities in database
        Act: Send GET request to /activities
        Assert: Response status is 200 and contains activities
        """
        # Arrange: client fixture is provided by conftest.py

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """
        Arrange: TestClient ready
        Act: Get activities from endpoint
        Assert: Response is a dictionary
        """
        # Arrange
        expected_keys = ["Chess Club", "Programming Class", "Gym Class"]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert isinstance(activities, dict)
        for key in expected_keys:
            assert key in activities

    def test_activity_has_required_fields(self, client):
        """
        Arrange: TestClient ready
        Act: Fetch activities and check structure
        Assert: Each activity has required fields
        """
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity '{activity_name}' missing field '{field}'"

    def test_participants_is_list(self, client):
        """
        Arrange: TestClient ready
        Act: Get activities and inspect participants field
        Assert: Participants field is always a list
        """
        # Arrange: Assume at least one activity exists

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(
                activity_data["participants"], list
            ), f"Activity '{activity_name}' participants is not a list"

    def test_max_participants_is_integer(self, client):
        """
        Arrange: TestClient ready
        Act: Fetch activities
        Assert: max_participants is an integer
        """
        # Arrange: Assume activities exist

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert isinstance(
                activity_data["max_participants"], int
            ), f"Activity '{activity_name}' max_participants is not an integer"

    def test_activities_include_chess_club(self, client):
        """
        Arrange: TestClient ready
        Act: Get all activities
        Assert: Chess Club is in the response
        """
        # Arrange
        expected_activity = "Chess Club"

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert expected_activity in activities
        assert activities[expected_activity]["description"] is not None
