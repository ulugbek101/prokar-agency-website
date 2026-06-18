from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from apps.blog.models import Post
from .forms import FeedbackForm
from .models import Certificate, Staff
from .telegram import send_feedback_notification


def home(request):
    latest_posts = Post.objects.filter(is_active=True).prefetch_related('tags')[:3]
    staff_list = Staff.objects.all()
    certificates = Certificate.objects.filter(is_active=True)
    return render(request, 'home.html', {
        'latest_posts': latest_posts,
        'staff_list': staff_list,
        'certificates': certificates,
    })


def about(request):
    return render(request, 'about.html')


def staff_detail(request, slug):
    staff = get_object_or_404(Staff, slug=slug)
    return render(request, 'staff/detail.html', {'staff': staff})


def feedback_submit(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save()
            send_feedback_notification(feedback)
            if is_ajax:
                return JsonResponse({'success': True})
            messages.success(request, _('Ваше сообщение отправлено! Мы свяжемся с вами в ближайшее время.'))
        else:
            if is_ajax:
                return JsonResponse({'success': False, 'errors': form.errors})
            messages.error(request, _('Пожалуйста, проверьте правильность заполнения формы.'))
    if is_ajax:
        return JsonResponse({'success': False})
    return redirect(request.META.get('HTTP_REFERER', '/'))
