from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(UnfoldModelAdmin):
    list_display = ('full_name', 'phone', 'short_body', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    list_editable = ('is_read',)
    search_fields = ('full_name', 'phone', 'body')
    readonly_fields = ('full_name', 'phone', 'body', 'created_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Контакт', {
            'fields': ('full_name', 'phone'),
        }),
        ('Сообщение', {
            'fields': ('body',),
        }),
        ('Служебное', {
            'fields': ('is_read', 'created_at'),
        }),
    )

    def short_body(self, obj):
        return obj.body[:80] + '…' if len(obj.body) > 80 else obj.body
    short_body.short_description = 'Сообщение'

    def has_add_permission(self, request):
        return False
