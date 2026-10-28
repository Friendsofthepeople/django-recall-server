from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from recall_server.voting.models import OfficialVote, PublicVote


@admin.register(OfficialVote)
class OfficialVoteAdmin(admin.ModelAdmin):
    list_display = ('get_bill_number', 'get_bill_title', 'get_legislator_name', 'get_legislator_type', 'vote', 'date')
    list_filter = ('vote', 'date', 'legislator_content_type')
    search_fields = ('bill__title', 'bill__bill_number', 'session_name', 'reason')
    readonly_fields = ('date',)
    fieldsets = (
        (None, {
            'fields': ('bill', 'vote', 'date', 'session_name')
        }),
        ('Legislator', {
            'fields': ('legislator_content_type', 'legislator_object_id')
        }),
        ('Additional Information', {
            'fields': ('reason',)
        }),
    )
    
    def get_bill_number(self, obj):
        return obj.bill.bill_number
    get_bill_number.short_description = 'Bill Number'
    get_bill_number.admin_order_field = 'bill__bill_number'
    
    def get_bill_title(self, obj):
        return obj.bill.title
    get_bill_title.short_description = 'Bill Title'
    get_bill_title.admin_order_field = 'bill__title'
    
    def get_legislator_name(self, obj):
        return obj.get_legislator_name()
    get_legislator_name.short_description = 'Legislator'
    
    def get_legislator_type(self, obj):
        return obj.get_legislator_type()
    get_legislator_type.short_description = 'Type'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('bill', 'legislator_content_type')


@admin.register(PublicVote)
class PublicVoteAdmin(admin.ModelAdmin):
    list_display = ('get_bill_number', 'get_bill_title', 'get_user_name', 'vote', 'get_region_name', 'date')
    list_filter = ('vote', 'date', 'region')
    search_fields = ('bill__title', 'bill__bill_number', 'user__first_name', 'user__last_name', 'comment')
    readonly_fields = ('date',)
    fieldsets = (
        (None, {
            'fields': ('bill', 'user', 'vote', 'date')
        }),
        ('Additional Information', {
            'fields': ('comment', 'region')
        }),
    )
    
    def get_bill_number(self, obj):
        return obj.bill.bill_number
    get_bill_number.short_description = 'Bill Number'
    get_bill_number.admin_order_field = 'bill__bill_number'
    
    def get_bill_title(self, obj):
        return obj.bill.title
    get_bill_title.short_description = 'Bill Title'
    get_bill_title.admin_order_field = 'bill__title'
    
    def get_user_name(self, obj):
        if hasattr(obj.user, 'get_full_name'):
            return obj.user.get_full_name()
        return str(obj.user)
    get_user_name.short_description = 'Voter'
    get_user_name.admin_order_field = 'user__first_name'
    
    def get_region_name(self, obj):
        return obj.region.name
    get_region_name.short_description = 'Region'
    get_region_name.admin_order_field = 'region__name'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('bill', 'user', 'region')
