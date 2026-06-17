from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from apps.blog.models import Post
from .forms import FeedbackForm


def home(request):
    latest_posts = Post.objects.filter(is_active=True).prefetch_related('tags')[:3]
    return render(request, 'home.html', {'latest_posts': latest_posts})


def feedback_submit(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Ваше сообщение отправлено! Мы свяжемся с вами в ближайшее время.'))
        else:
            messages.error(request, _('Пожалуйста, проверьте правильность заполнения формы.'))
    return redirect(request.META.get('HTTP_REFERER', '/'))
