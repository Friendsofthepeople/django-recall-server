"""
Register custom models to the Django Admin site for the `voter` Django app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from recall_server.voter.models import VoterProfile


class VoterProfileInline(admin.StackedInline):
    """
    Inline admin for VoterProfile to be included in the User admin.
    """
    model = VoterProfile
    can_delete = False
    verbose_name_plural = 'Voter Profile'
    fk_name = 'user'
    fields = (
        'profile_picture',
        'bio',
        'county',
        'constituency',
        'ward',
        'notify_on_new_bills',
        'notify_on_bill_status_change',
        'notify_on_vote',
        'interests'
    )


class CustomUserAdmin(UserAdmin):
    """
    Custom User admin that includes the VoterProfile inline.
    """
    inlines = (VoterProfileInline, )
    list_display = (
            'username',
            'email',
            'first_name',
            'last_name',
            'is_staff',
            'get_county'
            )
    list_select_related = ('voter_profile', )
    
    def get_county(self, instance):
        return instance.voter_profile.county\
                if hasattr(instance, 'voter_profile') and\
                instance.voter_profile.county else None
    get_county.short_description = 'County'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


@admin.register(VoterProfile)
class VoterProfileAdmin(admin.ModelAdmin):
    """
    Admin for the VoterProfile model.
    """
    list_display = (
            'get_username',
            'get_email',
            'get_full_name',
            'county',
            'constituency',
            'ward'
            )
    list_filter = (
            'county',
            'constituency',
            'notify_on_new_bills',
            'notify_on_bill_status_change',
            'notify_on_vote'
            )
    search_fields = (
            'user__username',
            'user__email',
            'user__first_name',
            'user__last_name',
            'bio',
            'interests'
            )
    readonly_fields = ('tokenized_id', 'created_at', 'updated_at')
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'
    get_username.admin_order_field = 'user__username'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'user__first_name'


# Legacy admin for backward compatibility
# @admin.register(Voter)
# class VoterAdmin(admin.ModelAdmin):
#     """
#     Legacy admin for the Voter model.
#     This is kept for backward compatibility and will be deprecated.
#     """
#     list_display = (
#             'username',
#             'email',
#             'first_name',
#             'last_name',
#             'county',
#             'constituency',
#             'is_verified'
#             )
#     list_filter = ('county', 'constituency', 'is_verified')
#     search_fields = ('username', 'email', 'first_name', 'last_name', 'bio')
#     readonly_fields = ('tokenized_id', 'created_at', 'date_joined')


# Unregister the default User admin and register our custom one
# admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
