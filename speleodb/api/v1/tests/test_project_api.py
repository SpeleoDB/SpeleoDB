import pytest
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized
from rest_framework import status
from rest_framework.test import APIClient

from speleodb.api.v1.serializers import ProjectSerializer
from speleodb.api.v1.tests.factories import PermissionFactory
from speleodb.api.v1.tests.factories import ProjectFactory
from speleodb.api.v1.tests.factories import TokenFactory
from speleodb.api.v1.tests.factories import UserFactory
from speleodb.surveys.models import Permission


@pytest.mark.parametrize(
    "level",
    [
        Permission.Level.ADMIN,
        Permission.Level.READ_AND_WRITE,
        Permission.Level.READ_ONLY,
    ],
)
class TestProjectInteraction(TestCase):
    """Token authentication"""

    header_prefix = "Token "

    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=False)

        self.user = UserFactory()
        self.token = TokenFactory(user=self.user)
        self.project = ProjectFactory()

    @parameterized.expand(
        [
            Permission.Level.ADMIN,
            Permission.Level.READ_AND_WRITE,
            Permission.Level.READ_ONLY,
        ]
    )
    def test_get_user_project(self, level):
        """
        Ensure POSTing json over token auth with correct
        credentials passes and does not require CSRF
        """

        _ = PermissionFactory(user=self.user, project=self.project, level=level)

        auth = self.header_prefix + self.token.key
        response = self.client.get(
            reverse("api:v1:one_project_apiview", kwargs={"id": self.project.id}),
            headers={"authorization": auth},
        )

        assert response.status_code == status.HTTP_200_OK, response.status_code

        # Verify data can be de-serialized
        serializer = ProjectSerializer(data=response.data["data"]["project"])
        assert serializer.is_valid(), (serializer.errors, response.data)

        serializer = ProjectSerializer(self.project, context={"user": self.user})

        assert serializer.data == response.data["data"]["project"], {
            "reserialized": serializer.data,
            "response_data": response.data["data"]["project"],
        }

        if isinstance(response.data["data"]["history"], (tuple, list)):
            commit_keys = [
                "author_email",
                "author_name",
                "authored_date",
                "committed_date",
                "committer_email",
                "committer_name",
                "created_at",
                "extended_trailers",
                "id",
                "message",
                "parent_ids",
                "short_id",
                "title",
                "trailers",
            ]
            for commit_data in response.data["data"]["history"]:
                assert all(key in commit_data for key in commit_keys), commit_data
                assert (
                    commit_data["committer_email"] == "contact@speleodb.com"
                ), commit_data["committer_email"]
                assert commit_data["committer_name"] == "SpeleoDB", commit_data[
                    "committer_name"
                ]
        else:
            # error fetching project from gitlab. TODO
            pass

    @parameterized.expand(
        [
            Permission.Level.ADMIN,
            Permission.Level.READ_AND_WRITE,
        ]
    )
    def test_acquire_and_release_user_project(self, level):
        """
        Ensure POSTing json over token auth with correct
        credentials passes and does not require CSRF
        """

        _ = PermissionFactory(user=self.user, project=self.project, level=level)

        # =================== ACQUIRE PROJECT =================== #

        # It is possible to acquire a project multiple time.
        for _ in range(5):
            auth = self.header_prefix + self.token.key
            response = self.client.post(
                reverse("api:v1:acquire_project", kwargs={"id": self.project.id}),
                headers={"authorization": auth},
            )

            assert response.status_code == status.HTTP_200_OK, response.status_code

            # refresh mutex data
            self.project.refresh_from_db()

            # Verify data can be de-serialized
            serializer = ProjectSerializer(data=response.data["data"])
            assert serializer.is_valid(), (serializer.errors, response.data)

            project_data = ProjectSerializer(
                self.project, context={"user": self.user}
            ).data

            assert project_data == response.data["data"], {
                "reserialized": project_data,
                "response_data": response.data["data"],
            }
            assert response.data["data"]["active_mutex"]["user"] == self.user.email, (
                response.data,
                self.user.email,
            )

        # =================== RELEASE PROJECT =================== #

        # It is possible to release a project multiple time.
        for _ in range(5):
            auth = self.header_prefix + self.token.key
            response = self.client.post(
                reverse("api:v1:release_project", kwargs={"id": self.project.id}),
                headers={"authorization": auth},
            )

            assert response.status_code == status.HTTP_200_OK, response.status_code

            # refresh mutex data
            self.project.refresh_from_db()

            # Verify data can be de-serialized
            serializer = ProjectSerializer(data=response.data["data"])
            assert serializer.is_valid(), (serializer.errors, response.data)

            project_data = ProjectSerializer(
                self.project, context={"user": self.user}
            ).data

            assert project_data == response.data["data"], {
                "reserialized": project_data,
                "response_data": response.data["data"],
            }
            assert response.data["data"]["active_mutex"] is None, response.data

    @parameterized.expand(
        [
            Permission.Level.ADMIN,
            Permission.Level.READ_AND_WRITE,
        ]
    )
    def test_acquire_and_release_user_project_with_comment(self, level):
        """
        Ensure POSTing json over token auth with correct
        credentials passes and does not require CSRF
        """

        _ = PermissionFactory(user=self.user, project=self.project, level=level)

        # =================== ACQUIRE PROJECT =================== #

        auth = self.header_prefix + self.token.key
        response = self.client.post(
            reverse("api:v1:acquire_project", kwargs={"id": self.project.id}),
            headers={"authorization": auth},
        )

        assert response.status_code == status.HTTP_200_OK, response.status_code

        # refresh mutex data
        self.project.refresh_from_db()

        # Verify data can be de-serialized
        serializer = ProjectSerializer(data=response.data["data"])
        assert serializer.is_valid(), (serializer.errors, response.data)

        project_data = ProjectSerializer(self.project, context={"user": self.user}).data

        assert project_data == response.data["data"], {
            "reserialized": project_data,
            "response_data": response.data["data"],
        }
        assert response.data["data"]["active_mutex"]["user"] == self.user.email, (
            response.data,
            self.user.email,
        )

        # =================== RELEASE PROJECT =================== #

        mutex = self.project.active_mutex

        test_comment = "hello world"

        auth = self.header_prefix + self.token.key
        response = self.client.post(
            reverse("api:v1:release_project", kwargs={"id": self.project.id}),
            headers={"authorization": auth},
            data={"comment": test_comment},
        )

        assert response.status_code == status.HTTP_200_OK, response.status_code

        # refresh mutex data
        mutex.refresh_from_db()
        self.project.refresh_from_db()

        # Verify data can be de-serialized
        serializer = ProjectSerializer(data=response.data["data"])
        assert serializer.is_valid(), (serializer.errors, response.data)

        project_data = ProjectSerializer(self.project, context={"user": self.user}).data

        assert project_data == response.data["data"], {
            "reserialized": project_data,
            "response_data": response.data["data"],
        }
        assert response.data["data"]["active_mutex"] is None, response.data
        assert mutex.closing_comment == test_comment, (mutex, test_comment)
        assert mutex.closing_user == self.user, (mutex, self.user)

    def test_fail_acquire_readonly_project(self):
        """
        Ensure POSTing json over token auth with correct
        credentials passes and does not require CSRF
        """

        _ = PermissionFactory(
            user=self.user, project=self.project, level=Permission.Level.READ_ONLY
        )

        auth = self.header_prefix + self.token.key
        response = self.client.post(
            reverse("api:v1:acquire_project", kwargs={"id": self.project.id}),
            headers={"authorization": auth},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN, response.status_code
        assert not response.data["success"], response.data

    def test_fail_release_readonly_project(self):
        _ = PermissionFactory(
            user=self.user, project=self.project, level=Permission.Level.READ_ONLY
        )

        auth = self.header_prefix + self.token.key
        response = self.client.post(
            reverse("api:v1:release_project", kwargs={"id": self.project.id}),
            headers={"authorization": auth},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN, response.status_code
        assert not response.data["success"], response.data
