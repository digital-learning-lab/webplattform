from dll.user.models import DllUser
import pytest
from django.test import Client, TestCase


class TestConstanceAdmin(TestCase):
    @pytest.fixture(autouse=True)
    def admin_client(self):
        self.client = Client()
        user = {
            "username": "alice",
            "first_name": "Alice",
            "last_name": "Doe",
            "email": "alice@blueshoe.de",
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
        }
        admin = DllUser.objects.create(**user)
        admin.set_password("password")
        admin.save()

    def test_admin_view_loads(self):
        self.client.login(username="alice@blueshoe.de", password="password")
        response = self.client.get("/admin/constance/config/")
        assert response.status_code == 200
