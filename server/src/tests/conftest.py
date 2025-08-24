import pytest
from mongomock_motor import AsyncMongoMockClient


@pytest.fixture
def db():
    client = AsyncMongoMockClient()
    db = client['engine']

    yield db

    client.close()
