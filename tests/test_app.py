from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Preserve original state for each test
original_activities = {name: {**data, "participants": list(data["participants"])} for name, data in activities.items()}


def setup_function():
    # Arrange: reset activities data before each test
    activities.clear()
    for name, data in original_activities.items():
        activities[name] = {**data, "participants": list(data["participants"])}


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert expected_activity in payload
    assert payload[expected_activity]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_registers_new_student():
    # Arrange
    activity_name = "Chess Club"
    new_student = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": new_student})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_student} for {activity_name}"}
    assert new_student in activities[activity_name]["participants"]


def test_signup_for_activity_returns_400_if_already_signed_up():
    # Arrange
    activity_name = "Chess Club"
    existing_student = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": existing_student})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_unknown_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Club"
    student = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": student})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_removes_student():
    # Arrange
    activity_name = "Chess Club"
    existing_student = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": existing_student})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {existing_student} from {activity_name}"}
    assert existing_student not in activities[activity_name]["participants"]


def test_unregister_non_registered_student_returns_400():
    # Arrange
    activity_name = "Chess Club"
    not_registered = "not_registered@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/unregister", params={"email": not_registered})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"


def test_root_redirects_to_static_index():
    # Arrange

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307 or response.status_code == 308
    assert response.headers["location"] == "/static/index.html"
