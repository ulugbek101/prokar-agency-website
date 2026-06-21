import uuid

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


class AIChatSession(models.Model):
    session_key = models.UUIDField(
        'Ключ устройства', unique=True, db_index=True, default=uuid.uuid4,
        help_text='UUID из localStorage браузера посетителя',
    )
    ip_address = models.GenericIPAddressField('IP-адрес', null=True, blank=True)
    user_agent = models.TextField('User-Agent', blank=True)
    created_at = models.DateTimeField('Начало переписки', auto_now_add=True)
    updated_at = models.DateTimeField('Последнее сообщение', auto_now=True)

    class Meta:
        verbose_name = 'AI-чат — сессия'
        verbose_name_plural = 'AI-чат — сессии'
        ordering = ['-updated_at']

    def __str__(self):
        return f'Сессия {str(self.session_key)[:8]}… | {self.ip_address or "—"}'

    @property
    def message_count(self):
        return self.messages.count()


class AIChatMessage(models.Model):
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_CHOICES = [(ROLE_USER, 'Пользователь'), (ROLE_ASSISTANT, 'AI')]

    session = models.ForeignKey(
        AIChatSession, on_delete=models.CASCADE,
        related_name='messages', verbose_name='Сессия',
    )
    role = models.CharField('Роль', max_length=16, choices=ROLE_CHOICES)
    content = models.TextField('Сообщение')
    created_at = models.DateTimeField('Время', auto_now_add=True)

    class Meta:
        verbose_name = 'AI-чат — сообщение'
        verbose_name_plural = 'AI-чат — сообщения'
        ordering = ['created_at']

    def __str__(self):
        label = 'Клиент' if self.role == self.ROLE_USER else 'AI'
        return f'[{label}] {self.content[:60]}'


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
