import pytest
from unittest.mock import MagicMock
from chat_functions import interpret_dream, get_dream_glance


@pytest.fixture
def mock_mongo(mocker):
    """Mock MongoDB"""
    mock_client = mocker.patch("chat_functions.MongoClient")
    mock_db = mock_client.return_value["mydatabase"]
    mock_users = mock_db["users"]
    return mock_users


@pytest.fixture
def mock_openai(mocker):
    """Mock OpenAI API"""
    mock_openai = mocker.patch("chat_functions.openai")
    mock_openai.chat.completions.create.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="This is a mock interpretation."))]
    )
    return mock_openai


def test_interpret_dream(mock_mongo, mock_openai):
    """Test the interpret_dream function"""
    mock_mongo.find_one.return_value = {
        "username": "test_user",
        "history": [{"role": "user", "content": "Previous dream"}],
    }

    result = interpret_dream("test_user", "This is a new dream.")

    assert result == "This is a mock interpretation."
    mock_openai.chat.completions.create.assert_called_once()


def test_interpret_dream_no_history(mock_mongo, mock_openai):
    """Test interpret_dream when the user has no history"""
    mock_mongo.find_one.return_value = None

    result = interpret_dream("new_user", "This is a new dream.")

    assert result == "This is a mock interpretation."
    mock_openai.chat.completions.create.assert_called_once()


def test_get_dream_glance(mock_mongo, mock_openai):
    """Test the get_dream_glance function"""
    mock_mongo.find_one.return_value = {
        "username": "test_user",
        "history": [{"role": "user", "content": "Previous dream"}],
    }

    result = get_dream_glance("test_user")

    assert result == "This is a mock interpretation."
    mock_openai.chat.completions.create.assert_called_once()
