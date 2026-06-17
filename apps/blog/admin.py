from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from modeltranslation.admin import TabbedTranslationAdmin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Post, Tag


class PostAdminForm(forms.ModelForm):
    """Custom form that applies CKEditor to both body fields and tag input."""

    body_ru = forms.CharField(
        widget=CKEditorUploadingWidget(),
        label='Содержание (рус)',
        required=False,
    )
    body_uz = forms.CharField(
        widget=CKEditorUploadingWidget(),
        label='Mazmun (uzb)',
        required=False,
    )

    tag_input = forms.CharField(
        required=False,
        label='Теги',
        help_text=(
            'Введите теги через запятую. Новые теги создаются автоматически. '
            'Пример: «Аудит, Налоговое право, IT Park» → #аудит, #налоговое_право, #it_park'
        ),
        widget=forms.TextInput(attrs={
            'placeholder': 'Аудит, Налоговое право, IT Park',
            'class': 'vTextField',
        }),
    )

    class Meta:
        model = Post
        fields = '__all__'
        exclude = ('tags',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            existing = ', '.join(t.name for t in self.instance.tags.all())
            self.fields['tag_input'].initial = existing


@admin.register(Tag)
class TagAdmin(UnfoldModelAdmin):
    list_display = ('display_name', 'post_count')
    search_fields = ('name',)

    def display_name(self, obj):
        return str(obj)
    display_name.short_description = 'Тег'

    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description = 'Публикаций'


@admin.register(Post)
class PostAdmin(TabbedTranslationAdmin, UnfoldModelAdmin):
    form = PostAdminForm
    list_display = ('title_ru', 'is_active', 'tag_list', 'created_at', 'view_on_site_link')
    list_filter = ('is_active', 'tags', 'created_at')
    search_fields = ('title_ru', 'title_uz', 'slug_ru', 'slug_uz')
    list_editable = ('is_active',)
    readonly_fields = ('created_at', 'updated_at', 'slug_ru', 'slug_uz', 'preview_link')
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Публикация', {
            'fields': (
                'is_active',
                'image',
                'tag_input',
                'preview_link',
            ),
        }),
        ('Русский', {
            'fields': ('title_ru', 'slug_ru', 'body_ru'),
        }),
        ('O\'zbek', {
            'fields': ('title_uz', 'slug_uz', 'body_uz'),
        }),
        ('Служебное', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def tag_list(self, obj):
        return ', '.join(str(t) for t in obj.tags.all())
    tag_list.short_description = 'Теги'

    def preview_link(self, obj):
        if obj.pk and (obj.slug_ru or obj.slug_uz):
            url = obj.get_absolute_url()
            return format_html(
                '<a href="{}" target="_blank" style="color:#0ea5e9">'
                '🔗 Открыть на сайте: {}</a>',
                url, url,
            )
        return '— сохраните публикацию для получения ссылки —'
    preview_link.short_description = 'Предпросмотр'

    def view_on_site_link(self, obj):
        if obj.pk and (obj.slug_ru or obj.slug_uz):
            return format_html(
                '<a href="{}" target="_blank">↗</a>', obj.get_absolute_url()
            )
        return '—'
    view_on_site_link.short_description = 'На сайте'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        tag_input = form.cleaned_data.get('tag_input', '')
        if tag_input is not None:
            tags = []
            for raw in tag_input.split(','):
                name = raw.strip()
                if name:
                    normalized = name.lower().replace(' ', '_')
                    tag, _ = Tag.objects.get_or_create(name=normalized)
                    tags.append(tag)
            obj.tags.set(tags)
