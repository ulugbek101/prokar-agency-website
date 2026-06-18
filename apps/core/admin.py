from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin as UnfoldModelAdmin

from .models import Certificate, Feedback, Staff


@admin.register(Feedback)
class FeedbackAdmin(UnfoldModelAdmin):
    list_display = ('full_name', 'phone', 'short_body', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    list_editable = ('is_read',)
    search_fields = ('full_name', 'phone', 'body')
    readonly_fields = ('full_name', 'phone', 'body', 'created_at')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Контакт', {'fields': ('full_name', 'phone')}),
        ('Сообщение', {'fields': ('body',)}),
        ('Служебное', {'fields': ('is_read', 'created_at')}),
    )

    def short_body(self, obj):
        return obj.body[:80] + '…' if len(obj.body) > 80 else obj.body
    short_body.short_description = 'Сообщение'

    def has_add_permission(self, request):
        return False


@admin.register(Staff)
class StaffAdmin(UnfoldModelAdmin):
    list_display = ('photo_preview', 'name', 'role', 'experience_years', 'order')
    list_editable = ('order',)
    list_display_links = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'role')

    fieldsets = (
        (None, {'fields': ('name', 'slug', 'role', 'photo', 'experience_years', 'order')}),
        ('Информация', {'fields': ('cert_primary', 'bio', 'other_certs')}),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;">', obj.photo.url)
        return '—'
    photo_preview.short_description = 'Фото'


@admin.register(Certificate)
class CertificateAdmin(UnfoldModelAdmin):
    list_display = ('image_preview', 'title', 'issued_date', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_display_links = ('title',)
    list_filter = ('is_active',)
    search_fields = ('title', 'description')

    fieldsets = (
        (None, {'fields': ('title', 'description', 'issued_date', 'is_active', 'order')}),
        ('Файлы', {'fields': ('image', 'file')}),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;border-radius:4px;">', obj.image.url)
        return '—'
    image_preview.short_description = 'Превью'
