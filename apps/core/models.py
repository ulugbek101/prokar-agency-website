from django.db import models
from django.urls import reverse


class Feedback(models.Model):
    full_name = models.CharField(max_length=255, verbose_name='Полное имя')
    phone = models.CharField(max_length=30, verbose_name='Телефон')
    body = models.TextField(verbose_name='Сообщение')
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Получено')

    class Meta:
        verbose_name = 'Обращение'
        verbose_name_plural = 'Обращения'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} — {self.created_at.strftime("%d.%m.%Y %H:%M")}'


class Staff(models.Model):
    name = models.CharField('ФИО', max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    role = models.CharField('Должность', max_length=200)
    photo = models.ImageField('Фото', upload_to='staff/', blank=True, null=True)
    experience_years = models.PositiveIntegerField('Опыт работы (лет)', default=0)
    cert_primary = models.TextField('Основной сертификат', blank=True)
    bio = models.TextField('Биография', blank=True)
    other_certs = models.TextField(
        'Другие сертификаты',
        blank=True,
        help_text='Каждый сертификат с новой строки',
    )
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Специалист'
        verbose_name_plural = 'Специалисты'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:staff_detail', kwargs={'slug': self.slug})

    @property
    def other_certs_list(self):
        return [ln.strip() for ln in self.other_certs.splitlines() if ln.strip()]


class Certificate(models.Model):
    title = models.CharField('Название', max_length=300)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Изображение', upload_to='certificates/')
    file = models.FileField(
        'Файл для скачивания (PDF)',
        upload_to='certificates/files/',
        blank=True,
        null=True,
    )
    issued_date = models.DateField('Дата выдачи', blank=True, null=True)
    is_active = models.BooleanField('Показывать', default=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ['order', 'title']
        verbose_name = 'Документ / Сертификат'
        verbose_name_plural = 'Документы и сертификаты'

    def __str__(self):
        return self.title
