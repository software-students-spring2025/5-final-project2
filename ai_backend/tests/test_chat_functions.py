import pytest
from unittest.mock import MagicMock
from chat_functions import interpret_dream, get_dream_glance


@pytest.fixture
def mock_mongo(mocker):
    mock_client = mocker.patch("chat_functions.MongoClient")
    mock_db = mock_client.return_value["mydatabase"]
    mock_users = mock_db["users"]
    return mock_users


@pytest.fixture
def mock_openai(mocker):
    mock_openai = mocker.patch("chat_functions.openai")
    mock_openai.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="This is a mock interpretation."))]
    )
    return mock_openai


def test_interpret_dream(mock_mongo, mock_openai):
    mock_mongo.find_one.return_value = {
        "username": "test_user",
        "history": [{"role": "user", "content": "Previous dream"}],
    }

    result = interpret_dream("test_user", "This is a new dream.")

    assert result == "This is a mock interpretation."
    mock_openai.chat.completions.create.assert_called_once()


def test_interpret_dream_no_history(mock_mongo, mock_openai):
    mock_mongo.find_one.return_value = None

    result = interpret_dream("new_user", "This is a new dream.")

    assert result == "This is a mock interpretation."
    mock_openai.chat.completions.create.assert_called_once()


def test_get_dream_glance(mock_mongo, mock_openai):
    dreams = [{"text": "Previous dream", "analysis": "Previous dream analysis"}]

    result = get_dream_glance(dreams)

    assert result == "This is a mock interpretation."
    mock_openai.chat.completions.create.assert_called_once()
