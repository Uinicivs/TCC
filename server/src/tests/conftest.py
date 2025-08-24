import pytest
from mongomock import MongoClient


@pytest.fixture
def connect_to_db():
    client = MongoClient()
    db = client['engine']

    yield db

    client.close()
