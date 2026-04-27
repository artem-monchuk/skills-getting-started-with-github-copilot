"""Tests for DELETE /activities/{activity_name}/unregister endpoint."""

import pytest
from urllib.parse import quote


class TestUnregister:
    """Test suite for unregistering students from activities."""

    def test_unregister_removes_participant_successfully(self, client):
        """
        Arrange: Student already registered in activity
        Act: Send DELETE request to unregister endpoint
        Assert: Response status is 200 and participant is removed
        """
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_response_contains_message(self, client):
        """
        Arrange: Registered participant
        Act: Unregister from activity
        Assert: Response contains the correct message
        """
        # Arrange
        email = "daniel@mergington.edu"  # In Chess Club
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_unregister_participant_no_longer_in_list(self, client):
        """
        Arrange: Participant in activity
        Act: Unregister student
        Assert: Participant no longer appears in activity's participant list
        """
        # Arrange
        email = "emma@mergington.edu"  # In Programming Class
        activity_name = "Programming Class"

        # Act
        client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        activities = client.get("/activities").json()

        # Assert
        participants = activities[activity_name]["participants"]
        assert email not in participants

    def test_unregister_decreases_participant_count(self, client):
        """
        Arrange: Get initial count for activity
        Act: Unregister a participant
        Assert: Participant count decreases by one
        """
        # Arrange
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities["Gym Class"]["participants"])
        email = "john@mergington.edu"  # In Gym Class
        activity_name = "Gym Class"

        # Act
        client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        updated_activities = client.get("/activities").json()

        # Assert
        updated_count = len(updated_activities[activity_name]["participants"])
        assert updated_count == initial_count - 1

    def test_unregister_nonexistent_participant_returns_404(self, client):
        """
        Arrange: Email that's not in activity
        Act: Try to unregister non-existent participant
        Assert: Response status is 404
        """
        # Arrange
        email = "nonexistent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Activity that doesn't exist
        Act: Try to unregister from non-existent activity
        Assert: Response status is 404
        """
        # Arrange
        email = "any@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_then_signup_again(self, client):
        """
        Arrange: Participant in activity
        Act: Unregister, then signup again
        Assert: Both operations succeed, participant is back in list
        """
        # Arrange
        email = "sophia@mergington.edu"  # In Programming Class
        activity_name = "Programming Class"

        # Act: Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Re-signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        activities = client.get("/activities").json()

        # Assert
        assert unregister_response.status_code == 200
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_unregister_increases_available_spots(self, client):
        """
        Arrange: Get initial available spots
        Act: Unregister a participant
        Assert: Available spots increase
        """
        # Arrange
        activities_before = client.get("/activities").json()
        activity_name = "Soccer Team"
        initial_spots = (
            activities_before[activity_name]["max_participants"]
            - len(activities_before[activity_name]["participants"])
        )
        email = "lucas@mergington.edu"  # In Soccer Team

        # Act
        client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        activities_after = client.get("/activities").json()

        # Assert
        updated_spots = (
            activities_after[activity_name]["max_participants"]
            - len(activities_after[activity_name]["participants"])
        )
        assert updated_spots == initial_spots + 1

    def test_unregister_one_participant_keeps_others(self, client):
        """
        Arrange: Activity with multiple participants
        Act: Unregister one participant
        Assert: Other participants remain unchanged
        """
        # Arrange
        activity_name = "Chess Club"
        activities = client.get("/activities").json()
        initial_participants = set(activities[activity_name]["participants"])
        email_to_remove = "michael@mergington.edu"
        other_participants = initial_participants - {email_to_remove}

        # Act
        client.delete(
            f"/activities/{activity_name}/unregister?email={email_to_remove}"
        )
        updated_activities = client.get("/activities").json()

        # Assert
        updated_participants = set(updated_activities[activity_name]["participants"])
        assert updated_participants == other_participants
        assert email_to_remove not in updated_participants

    def test_unregister_with_special_characters_in_email(self, client):
        """
        Arrange: First signup a student with special characters, then unregister
        Act: Signup then unregister special character email using proper URL encoding
        Assert: Both operations work correctly
        """
        # Arrange
        email = "test+special@mergington.edu"
        activity_name = "Debate Team"
        
        # First signup - Use quote() to properly encode the + character
        client.post(
            f"/activities/{activity_name}/signup?email={quote(email)}"
        )

        # Act: Unregister with proper encoding
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={quote(email)}"
        )
        activities = client.get("/activities").json()

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
