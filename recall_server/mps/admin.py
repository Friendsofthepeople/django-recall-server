"""
Register custom models to the Django Admin site for the `mps` Django app.
"""
from django.contrib import admin

from recall_server.mps.models import MemberOfParliament


admin.site.register(MemberOfParliament)
