"""Tests for POST /activities/{activity_name}/signup endpoint."""

import pytest
from urllib.parse import quote


class TestSignup:
    """Test suite for student signup to activities."""

    def test_signup_adds_participant_successfully(self, client):
        """
        Arrange: Setup new email and activity name
        Act: Send POST request to signup endpoint
        Assert: Response status is 200 and participant is added
        """
        # Arrange
        email = "test.student@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_response_contains_message(self, client):
        """
        Arrange: New email and activity
        Act: Signup student
        Assert: Response contains success message
        """
        # Arrange
        email = "alice@mergington.edu"
        activity_name = "Programming Class"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_duplicate_returns_error(self, client):
        """
        Arrange: Student already in participants list
        Act: Try to signup same student again
        Assert: Response status is 400 and error message is returned
        """
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, client):
        """
        Arrange: Activity name that doesn't exist
        Act: Try to signup for non-existent activity
        Assert: Response status is 404 and error detail is provided
        """
        # Arrange
        email = "new.student@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_participant_appears_in_activity(self, client):
        """
        Arrange: New student email and valid activity
        Act: Signup student, then fetch activities
        Assert: New participant appears in activity's participant list
        """
        # Arrange
        email = "bob@mergington.edu"
        activity_name = "Gym Class"

        # Act
        client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        activities_response = client.get("/activities")
        activities = activities_response.json()

        # Assert
        participants = activities[activity_name]["participants"]
        assert email in participants

    def test_signup_increases_participant_count(self, client):
        """
        Arrange: Get initial participant count for an activity
        Act: Signup new student
        Assert: Participant count increases by one
        """
        # Arrange
        initial_activities = client.get("/activities").json()
        initial_count = len(initial_activities["Soccer Team"]["participants"])
        email = "carol@mergington.edu"
        activity_name = "Soccer Team"

        # Act
        client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        updated_activities = client.get("/activities").json()

        # Assert
        updated_count = len(updated_activities[activity_name]["participants"])
        assert updated_count == initial_count + 1

    def test_signup_with_special_characters_in_email(self, client):
        """
        Arrange: Email with special characters
        Act: Signup with special character email using proper URL encoding
        Assert: Signup succeeds (email is properly encoded)
        """
        # Arrange
        email = "test+special@mergington.edu"
        activity_name = "Basketball Club"

        # Act - Use quote() to properly encode the + character
        response = client.post(
            f"/activities/{activity_name}/signup?email={quote(email)}"
        )

        # Assert
        assert response.status_code == 200
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

    def test_signup_different_students_same_activity(self, client):
        """
        Arrange: Two different students
        Act: Signup both to same activity
        Assert: Both appear in participants list
        """
        # Arrange
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        activity_name = "Art Workshop"

        # Act
        client.post(
            f"/activities/{activity_name}/signup?email={email1}"
        )
        client.post(
            f"/activities/{activity_name}/signup?email={email2}"
        )
        activities = client.get("/activities").json()

        # Assert
        participants = activities[activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants

    def test_signup_same_student_different_activities(self, client):
        """
        Arrange: One student, two different activities
        Act: Signup student to Activity A, then Activity B
        Assert: Both signups succeed, student in both activities
        """
        # Arrange
        email = "versatile@mergington.edu"
        activity1 = "Theater Club"
        activity2 = "Science Olympiad"

        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup?email={email}"
        )
        response2 = client.post(
            f"/activities/{activity2}/signup?email={email}"
        )
        activities = client.get("/activities").json()

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]
