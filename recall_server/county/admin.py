"""
Register custom models to the Django Admin site for the `county` Django app.
"""

from django.contrib import admin
from recall_server.county.models import Constituency, County, Senator, MCA

admin.site.register(County)
admin.site.register(Constituency)
admin.site.register(Senator)
admin.site.register(MCA)
