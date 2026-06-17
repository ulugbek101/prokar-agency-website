from django.db import models
from django.urls import reverse
from django.utils.translation import get_language
from ckeditor_uploader.fields import RichTextUploadingField
from slugify import slugify


class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def save(self, *args, **kwargs):
        self.name = self.name.strip().lower().replace(' ', '_')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'#{self.name}'


class Post(models.Model):
    # Title fields (base + translated by modeltranslation -> title_ru, title_uz)
    title = models.CharField(max_length=255, verbose_name='Заголовок')

    # Slug fields (base + translated -> slug_ru, slug_uz)
    slug = models.SlugField(max_length=300, blank=True, verbose_name='Slug')

    # Body fields defined explicitly so CKEditor widget applies reliably
    body_ru = RichTextUploadingField(verbose_name='Содержание (рус)', blank=True)
    body_uz = RichTextUploadingField(verbose_name='Mazmun (uzb)', blank=True)

    # Featured image
    image = models.ImageField(
        upload_to='posts/covers/', blank=True, null=True,
        verbose_name='Обложка',
    )

    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Теги')
    is_active = models.BooleanField(default=False, verbose_name='Активна')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-created_at']

    def _unique_slug(self, base, field_name):
        slug = base
        counter = 1
        qs = Post.objects.exclude(pk=self.pk)
        while qs.filter(**{field_name: slug}).exists():
            slug = f'{base}-{counter}'
            counter += 1
        return slug

    def save(self, *args, **kwargs):
        if self.title_ru and not self.slug_ru:
            base = slugify(self.title_ru, allow_unicode=False)
            self.slug_ru = self._unique_slug(base, 'slug_ru')
        if self.title_uz and not self.slug_uz:
            base = slugify(self.title_uz, allow_unicode=False)
            self.slug_uz = self._unique_slug(base, 'slug_uz')
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        lang = get_language()
        slug = self.slug_uz if lang == 'uz' and self.slug_uz else self.slug_ru
        return reverse('blog:post_detail', kwargs={'slug': slug})

    @property
    def body(self):
        lang = get_language()
        return self.body_uz if lang == 'uz' and self.body_uz else self.body_ru

    def __str__(self):
        return self.title_ru or self.title_uz or f'Post #{self.pk}'
