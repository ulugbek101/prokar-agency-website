from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from unfold.admin import TabularInline

from .models import AIChatMessage, AIChatSession, Certificate, Feedback, Staff


class AIChatMessageInline(TabularInline):
    model = AIChatMessage
    extra = 0
    readonly_fields = ('role', 'short_content', 'created_at')
    fields = ('role', 'short_content', 'created_at')
    can_delete = False
    show_change_link = False

    def short_content(self, obj):
        text = obj.content
        if len(text) > 200:
            text = text[:200] + '…'
        color = '#0B1E3D' if obj.role == 'user' else '#7D1C1C'
        return format_html('<span style="color:{}">{}</span>', color, text)
    short_content.short_description = 'Текст'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(AIChatSession)
class AIChatSessionAdmin(UnfoldModelAdmin):
    list_display = ('short_key', 'ip_address', 'msg_count', 'first_user_msg', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('session_key', 'ip_address', 'user_agent')
    readonly_fields = ('session_key', 'ip_address', 'user_agent', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
    inlines = [AIChatMessageInline]

    fieldsets = (
        ('Устройство', {'fields': ('session_key', 'ip_address', 'user_agent')}),
        ('Время', {'fields': ('created_at', 'updated_at')}),
    )

    def short_key(self, obj):
        return str(obj.session_key)[:8] + '…'
    short_key.short_description = 'Сессия'

    def msg_count(self, obj):
        return obj.message_count
    msg_count.short_description = 'Сообщений'

    def first_user_msg(self, obj):
        msg = obj.messages.filter(role='user').first()
        if msg:
            return msg.content[:60] + ('…' if len(msg.content) > 60 else '')
        return '—'
    first_user_msg.short_description = 'Первый вопрос'

    def has_add_permission(self, request):
        return False


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
