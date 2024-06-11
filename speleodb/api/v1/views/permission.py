#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from speleodb.api.v1.permissions import UserHasAdminAccess
from speleodb.api.v1.permissions import UserHasReadAccess
from speleodb.api.v1.serializers import PermissionListSerializer
from speleodb.api.v1.serializers import PermissionSerializer
from speleodb.api.v1.serializers import ProjectSerializer
from speleodb.surveys.models import Permission
from speleodb.surveys.models import Project
from speleodb.users.models import User
from speleodb.utils.view_cls import CustomAPIView


class ProjectPermissionListView(CustomAPIView):
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated, UserHasReadAccess]
    serializer_class = ProjectSerializer
    http_method_names = ["get"]
    lookup_field = "id"

    def _get(self, request, *args, **kwargs):
        project = self.get_object()
        permissions = project.get_all_permissions()

        project_serializer = ProjectSerializer(project, context={"user": request.user})
        permission_serializer = PermissionListSerializer(permissions)

        return {
            "project": project_serializer.data,
            "permissions": permission_serializer.data,
        }


class ProjectPermissionView(CustomAPIView):
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated, UserHasAdminAccess]
    serializer_class = ProjectSerializer
    http_method_names = ["post", "put", "delete"]
    lookup_field = "id"

    def _process_request_data(self, data, skip_level=False):
        perm_data = {}
        for key in ["user", "level"]:
            try:
                if key == "level" and skip_level:
                    continue

                value = data[key]

                if key == "level":
                    if not isinstance(value, str) or value.upper() not in [
                        name for _, name in Permission.Level.choices
                    ]:
                        return Response(
                            {"error": f"Invalid value received for `{key}`: `{value}`"},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    perm_data[key] = getattr(Permission.Level, value.upper())

                elif key in "user":
                    try:
                        perm_data[key] = User.objects.get(email=value)
                    except ObjectDoesNotExist:
                        return Response(
                            {"error": f"The user: `{value}` does not exist."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    if not perm_data[key].is_active:
                        return Response(
                            {"error": f"The user: `{value}` is inactive."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )

            except KeyError:
                return Response(
                    {"error": f"Attribute: `{key}` is missing"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return perm_data

    def _post(self, request, *args, **kwargs):
        project = self.get_object()

        perm_data = self._process_request_data(data=request.data)

        # An Error occured
        if isinstance(perm_data, Response):
            return perm_data

        permission, created = Permission.objects.get_or_create(
            project=project, user=perm_data["user"]
        )

        if not created and permission.is_active:
            return Response(
                {
                    "error": (
                        f"A permission for this user: `{perm_data['user']}` "
                        "already exist."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        permission.reactivate(level=perm_data["level"])

        permission_serializer = PermissionSerializer(permission)
        project_serializer = ProjectSerializer(project, context={"user": request.user})

        return Response(
            {
                "project": project_serializer.data,
                "permission": permission_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def _put(self, request, *args, **kwargs):
        project = self.get_object()

        perm_data = self._process_request_data(data=request.data)

        # An Error occured
        if isinstance(perm_data, Response):
            return perm_data

        try:
            permission = Permission.objects.get(project=project, user=perm_data["user"])
        except ObjectDoesNotExist:
            return Response(
                {
                    "error": (
                        f"A permission for this user: `{perm_data['user']}` "
                        "does not exist."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not permission.is_active:
            return Response(
                {
                    "error": (
                        f"The permission for this user: `{perm_data['user']}` "
                        "is inactive. Recreate the permission."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        permission.level = perm_data["level"]
        permission.save()

        permission_serializer = PermissionSerializer(permission)
        project_serializer = ProjectSerializer(project, context={"user": request.user})

        return Response(
            {
                "project": project_serializer.data,
                "permission": permission_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def _delete(self, request, *args, **kwargs):
        project = self.get_object()

        perm_data = self._process_request_data(data=request.data, skip_level=True)

        # An Error occured
        if isinstance(perm_data, Response):
            return perm_data

        try:
            permission = Permission.objects.get(project=project, user=perm_data["user"])
        except ObjectDoesNotExist:
            return Response(
                {
                    "error": (
                        f"A permission for this user: `{perm_data['user']}` "
                        "does not exist."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        permission.deactivate(user=request.user)
        project_serializer = ProjectSerializer(project, context={"user": request.user})

        return Response(
            {
                "project": project_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )
