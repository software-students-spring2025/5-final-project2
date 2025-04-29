import pytest
from openai_app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_chat_functions(mocker):
    mock_chat = mocker.patch("openai_app.chat_functions")
    mock_chat.interpret_dream.return_value = "This is a mock interpretation."
    mock_chat.get_dream_glance.return_value = "This is a mock dream glance."
    return mock_chat


def test_interpret_success(client, mock_chat_functions):
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
    response = client.post("/interpret", json={"username": "test_user"})
    assert response.status_code == 400
    assert response.json == {"error": "No dream provided"}


def test_interpret_exception(client, mock_chat_functions):
    mock_chat_functions.interpret_dream.side_effect = Exception("Mock error")
    response = client.post(
        "/interpret",
        json={"username": "test_user", "dream": "I had a strange dream."},
    )
    assert response.status_code == 500
    assert response.json == {"error": "Mock error"}


def test_dream_glance_success(client, mock_chat_functions):
    mock_user_data = {
        "username": "test_user",
        "dreams": [
            {"text": "Dream 1", "analysis": "Analysis 1"},
            {"text": "Dream 2", "analysis": "Analysis 2"},
        ],
    }
    mock_chat_functions.users.find_one.return_value = mock_user_data

    response = client.get("/dream_glance", query_string={"username": "test_user"})
    assert response.status_code == 200


def test_dream_glance_no_username(client):
    """Test the /dream_glance endpoint with no username provided."""
    response = client.get("/dream_glance")
    assert response.status_code == 400
    assert response.json == {"summary": "No username provided."}


def test_dream_glance_no_dreams(client, mock_chat_functions):
    mock_chat_functions.users.find_one.return_value = {"username": "test_user", "dreams": []}

    response = client.get("/dream_glance", query_string={"username": "test_user"})
    assert response.status_code == 200
    assert response.json == {"summary": "No dreams found yet."}
    mock_chat_functions.get_dream_glance.assert_not_called()