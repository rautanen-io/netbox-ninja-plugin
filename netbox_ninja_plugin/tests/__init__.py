# pylint: disable=missing-function-docstring
from django.http import HttpResponse
from django.test import Client, TestCase
from django.urls import reverse
from users.models import User


class TestNinjaTemplateMixing(TestCase):

    def get(
        self,
        url_name: str,
        pk: int = 0,
    ) -> HttpResponse:
        url = reverse(
            f"plugins:netbox_ninja_plugin:{url_name}", kwargs={"pk": pk} if pk else {}
        )
        return self.client.get(url)

    def setUp(self) -> None:
        User.objects.create_superuser("ninja", "ninja@rautanen.io", "ninja")
        self.client = Client()
        self.client.login(username="ninja", password="ninja")
