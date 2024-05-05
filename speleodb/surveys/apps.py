import contextlib

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SurveysConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "speleodb.surveys"
    verbose_name = _("Surveys")

    def ready(self):
        with contextlib.suppress(ImportError):
            import speleodb.users.signals  # noqa: F401
