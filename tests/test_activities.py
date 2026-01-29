"""Tests for the activities API endpoints"""

import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities(self, client, reset_activities):
        """Test that the activities endpoint returns all activities"""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check that all activities are present
        assert "Basketball Team" in data
        assert "Soccer Club" in data
        assert "Drama Club" in data
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
        
    def test_get_activities_structure(self, client, reset_activities):
        """Test that each activity has the correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
            
    def test_activities_have_pre_existing_participants(self, client, reset_activities):
        """Test that some activities have pre-existing participants"""
        response = client.get("/activities")
        data = response.json()
        
        # Check that Chess Club has participants
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
        
        # Check that Basketball Team has no participants
        assert len(data["Basketball Team"]["participants"]) == 0


class TestSignup:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "test@mergington.edu" in data["message"]
        assert "Basketball Team" in data["message"]
        
    def test_signup_updates_participants(self, client, reset_activities):
        """Test that signup updates the participants list"""
        email = "newstudent@mergington.edu"
        
        # Signup
        response = client.post(
            f"/activities/Soccer%20Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was added
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data["Soccer Club"]["participants"]
        
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Fake%20Activity/signup?email=test@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
        
    def test_signup_duplicate_email(self, client, reset_activities):
        """Test signup with duplicate email"""
        email = "michael@mergington.edu"
        
        # Try to signup with email already in Chess Club
        response = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
        
    def test_signup_multiple_students(self, client, reset_activities):
        """Test multiple students can signup for the same activity"""
        activity = "Art Workshop"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # First signup
        response1 = client.post(
            f"/activities/Art%20Workshop/signup?email={email1}"
        )
        assert response1.status_code == 200
        
        # Second signup
        response2 = client.post(
            f"/activities/Art%20Workshop/signup?email={email2}"
        )
        assert response2.status_code == 200
        
        # Verify both are in participants
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email1 in data[activity]["participants"]
        assert email2 in data[activity]["participants"]
        assert len(data[activity]["participants"]) == 2


class TestUnregister:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client, reset_activities):
        """Test successful unregister from an activity"""
        email = "michael@mergington.edu"
        
        # Verify participant exists
        response = client.get("/activities")
        assert email in response.json()["Chess Club"]["participants"]
        
        # Unregister
        response = client.post(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
    def test_unregister_updates_participants(self, client, reset_activities):
        """Test that unregister removes participant from list"""
        email = "daniel@mergington.edu"
        
        # Unregister
        response = client.post(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email not in data["Chess Club"]["participants"]
        
    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.post(
            "/activities/Fake%20Activity/unregister?email=test@mergington.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
        
    def test_unregister_email_not_registered(self, client, reset_activities):
        """Test unregister for email not in activity"""
        response = client.post(
            "/activities/Basketball%20Team/unregister?email=notregistered@mergington.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
        
    def test_unregister_and_signup_again(self, client, reset_activities):
        """Test that a student can unregister and sign up again"""
        email = "test@mergington.edu"
        activity = "Soccer Club"
        
        # First signup
        response1 = client.post(
            f"/activities/Soccer%20Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.post(
            f"/activities/Soccer%20Club/unregister?email={email}"
        )
        assert response2.status_code == 200
        
        # Signup again
        response3 = client.post(
            f"/activities/Soccer%20Club/signup?email={email}"
        )
        assert response3.status_code == 200
        
        # Verify participant is in list
        activities_response = client.get("/activities")
        data = activities_response.json()
        assert email in data[activity]["participants"]


class TestRoot:
    """Tests for the root endpoint"""

    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
