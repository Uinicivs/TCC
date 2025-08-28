import pytest
from mongomock_motor import AsyncMongoMockClient


@pytest.fixture
def db():
    client = AsyncMongoMockClient(tz_aware=True)
    db = client['engine']

    yield db

    client.close()
