import random

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from speleodb.api.v1.tests.factories import PermissionFactory
from speleodb.api.v1.tests.factories import TokenFactory
from speleodb.api.v1.tests.factories import UserFactory
from speleodb.surveys.models import Permission


class TestProjectInteraction(TestCase):
    """Token authentication"""

    header_prefix = "Token "
    PROJECT_COUNT = 10

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=False)

        self.user = UserFactory()
        self.token = TokenFactory(user=self.user)

    def test_get_user_projects(self):
        """
        Ensure POSTing json over token auth with correct
        credentials passes and does not require CSRF
        """

        for _ in range(self.PROJECT_COUNT):
            # automatically creates projects associated
            _ = PermissionFactory(
                user=self.user,
                level=random.choice(list(Permission.Level)),
            )

        endpoint = reverse("api:v1:list_all_projects")

        auth = self.header_prefix + self.token.key
        response = self.client.get(endpoint, headers={"authorization": auth})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == self.PROJECT_COUNT

        attributes = [
            "creation_date",
            "description",
            "fork_from",
            "id",
            "latitude",
            "longitude",
            "modified_date",
            "active_mutex",
            "name",
            "permission",
        ]

        for project in response.data["data"]:
            assert all(attr in project for attr in attributes)

        target = {
            "success": True,
            "url": f"http://testserver{endpoint}",
        }

        for key, val in target.items():
            assert val == response.data[key]
