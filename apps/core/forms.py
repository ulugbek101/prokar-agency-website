from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('full_name', 'phone', 'body')
        labels = {
            'full_name': _('Ваше имя'),
            'phone': _('Телефон'),
            'body': _('Сообщение'),
        }
        widgets = {
            'full_name': forms.TextInput(attrs={
                'placeholder': _('Иван Иванов'),
                'class': 'feedback-input',
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': '+998 90 000 00 00',
                'class': 'feedback-input',
            }),
            'body': forms.Textarea(attrs={
                'placeholder': _('Опишите ваш вопрос или задачу…'),
                'rows': 4,
                'class': 'feedback-input',
            }),
        }
