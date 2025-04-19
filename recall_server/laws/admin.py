from django.contrib import admin

from recall_server.laws.models import Bill, House, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_at', 'updated_at', 'likes_count', 'reported_count')
    fields = ('user', 'comment', 'is_featured', 'is_approved', 'likes_count', 'reported_count', 'created_at')


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('bill_number', 'title', 'house', 'stage', 'status', 'deadline_for_voting', 'created_at')
    list_filter = ('house', 'stage', 'status', 'proposed_date')
    search_fields = ('title', 'description', 'bill_number', 'tags')
    readonly_fields = ('created_at', 'updated_at', 'yes_votes_count', 'no_votes_count', 'abstain_votes_count',
                      'public_yes_votes', 'public_no_votes', 'public_abstain_votes')
    fieldsets = (
        (None, {
            'fields': ('bill_id', 'bill_number', 'title', 'house', 'stage', 'status', 'deadline_for_voting')
        }),
        ('Content', {
            'fields': ('description', 'summary', 'impact_analysis', 'tags')
        }),
        ('Tracking', {
            'fields': ('proposed_date', 'created_at', 'updated_at', 'stage_history')
        }),
        ('Vote Counts', {
            'fields': (('yes_votes_count', 'no_votes_count', 'abstain_votes_count'),
                      ('public_yes_votes', 'public_no_votes', 'public_abstain_votes'))
        }),
    )
    inlines = [CommentInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('house')


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'house_id', 'get_bills_count')
    search_fields = ('name',)
    
    def get_bills_count(self, obj):
        return obj.bills.count()
    get_bills_count.short_description = 'Bills Count'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'bill', 'is_featured', 'is_approved', 'likes_count', 'reported_count', 'created_at')
    list_filter = ('is_featured', 'is_approved', 'created_at')
    search_fields = ('comment', 'user__first_name', 'user__last_name', 'bill__title')
    readonly_fields = ('created_at', 'updated_at', 'likes_count', 'reported_count')
    list_editable = ('is_featured', 'is_approved')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'bill')
