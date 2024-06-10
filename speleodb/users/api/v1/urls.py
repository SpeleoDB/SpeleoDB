#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.urls import path

from speleodb.users.api.v1.views import ObtainAuthToken
from speleodb.users.api.v1.views import UserInfo
from speleodb.users.api.v1.views import UserPasswordChangeView
from speleodb.users.api.v1.views import UserPreference

app_name = "user_api"

urlpatterns = [
    path("user/auth-token/", ObtainAuthToken.as_view(), name="get_auth_token"),
    path("user/info/", UserInfo.as_view(), name="set_user_info"),
    path("user/preferences/", UserPreference.as_view(), name="set_user_preferences"),
    path(
        "user/password/", UserPasswordChangeView.as_view(), name="change_user_password"
    ),
]