from modeltranslation.translator import register, TranslationOptions
from .models import Post


@register(Post)
class PostTranslationOptions(TranslationOptions):
    # Generates title_ru, title_uz, slug_ru, slug_uz fields
    fields = ('title', 'slug')
    required_languages = {
        'ru': ('title',),
        'uz': ('title',),
    }
