"""
Custom config settings for the `common` Django app.
"""

from django.apps import AppConfig


class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recall_server.common"
