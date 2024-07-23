"""
Register custom models to the Django Admin site for the `recall` Django app.
"""

from django.contrib import admin

from .models import Recall

admin.site.register(Recall)
