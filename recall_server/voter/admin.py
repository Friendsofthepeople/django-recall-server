from django.contrib import admin

from .models import Voter

class VoterAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "is_active", "created_at")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("is_active", "created_at")

fielsets = (
    (None, {
        "fields": ("first_name", "last_name", "email")
    }),
    ("permissions", {"fields": ("is_active",)}),
    ("Important dates", {"fields":("created_at",)}),
)

# Register your models here.
admin.site.register(Voter, VoterAdmin)
