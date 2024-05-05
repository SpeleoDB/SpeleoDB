from django.conf import settings
from django.conf.urls import include
from django.urls import re_path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from speleodb.users.api.views import UserViewSet

user_router = DefaultRouter() if settings.DEBUG else SimpleRouter()
user_router.register("users", UserViewSet)

urlpatterns = [
    re_path(r"^v1/", include("speleodb.surveys.api.v1.urls")),
]


app_name = "api"
urlpatterns += user_router.urls
