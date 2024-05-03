#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.urls import path

from speleodb.surveys.api.v1.views import ProjectAcquireApiView
from speleodb.surveys.api.v1.views import ProjectApiView
from speleodb.surveys.api.v1.views import ProjectListApiView
from speleodb.surveys.api.v1.views import ProjectReleaseApiView

urlpatterns = [
    # ========================== Public API Routes ========================== #
    # ================== Authentication Required API Routes ================= #
    path("projects/", ProjectListApiView.as_view()),
    path("project/<uuid:project_id>/", ProjectApiView.as_view()),
    path("project/<uuid:project_id>/acquire/", ProjectAcquireApiView.as_view()),
    path("project/<uuid:project_id>/release/", ProjectReleaseApiView.as_view()),
    # ================ Private API Routes - API KEY REQUIRED ================ #
]