from django.contrib import admin

from recall_server.county.models import County, Constituency


admin.site.register(County)
admin.site.register(Constituency)
