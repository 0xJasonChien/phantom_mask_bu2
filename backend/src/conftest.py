import pytest
from rest_framework.test import APIClient

from account.models import User


@pytest.fixture
def test_user() -> User:
    user = User(
        email='testuser@example.com',
        username='testuser',
    )
    user.set_password('testpass123')
    user.save()
    return user


@pytest.fixture
def authenticated_client(test_user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=test_user)
    return client
