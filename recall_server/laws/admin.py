from django.contrib import admin

from recall_server.laws.models import Bill, House


admin.site.register(Bill)
admin.site.register(House)
