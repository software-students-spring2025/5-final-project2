import pytest
from openai_app import app


@pytest.fixture
def client():
    """Flask test client"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_chat_functions(mocker):
    """Mock chat_functions"""
    mock_chat = mocker.patch("openai_app.chat_functions")
    mock_chat.interpret_dream.return_value = "This is a mock interpretation."
    mock_chat.get_dream_glance.return_value = "This is a mock dream glance."
    return mock_chat


def test_interpret_success(client, mock_chat_functions):
    """Test interpret endpoint"""
    response = client.post(
        "/interpret",
        json={"username": "test_user", "dream": "I had a strange dream."},
    )
    assert response.status_code == 200
    assert response.json == {"interpretation": "This is a mock interpretation."}
    mock_chat_functions.interpret_dream.assert_called_once_with(
        "test_user", "I had a strange dream."
    )


def test_interpret_no_dream(client):
    """Test interpret endpoint with missing input"""
    response = client.post("/interpret", json={"username": "test_user"})
    assert response.status_code == 400
    assert response.json == {"error": "No dream provided"}


def test_interpret_exception(client, mock_chat_functions):
    """Test the interpret endpoint when exception is raised"""
    mock_chat_functions.interpret_dream.side_effect = Exception("Mock error")
    response = client.post(
        "/interpret",
        json={"username": "test_user", "dream": "I had a strange dream."},
    )
    assert response.status_code == 500
    assert response.json == {"error": "Mock error"}


def test_glance_success(client, mock_chat_functions):
    """Test the glance endpoint"""
    response = client.post("/glance", json={"username": "test_user"})
    assert response.status_code == 200
    assert response.json == {"dream_glance": "This is a mock dream glance."}
    mock_chat_functions.get_dream_glance.assert_called_once_with("test_user")


def test_glance_exception(client, mock_chat_functions):
    """Test the glance endpoint when exception is raised"""
    mock_chat_functions.get_dream_glance.side_effect = Exception("Mock error")
    response = client.post("/glance", json={"username": "test_user"})
    assert response.status_code == 500
    assert response.json == {"error": "Mock error"}
