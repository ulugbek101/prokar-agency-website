import json
import uuid as _uuid

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from apps.blog.models import Post
from .forms import FeedbackForm
from .models import AIChatMessage, AIChatSession, Certificate, Staff
from .telegram import send_feedback_notification

_AI_SYSTEM_PROMPT = """Вы — AI-консультант компании ООО «Прокар Эксперт Аудит» (Prokar Ekspert Audit).

О компании:
- Полное название: ООО «Прокар Эксперт Аудит»
- 22 года опыта на рынке Узбекистана (с 2002 года)
- Более 500 клиентов, 89% лояльности
- Официальная лицензия №00818, Аудиторская палата РУз, ISO 9001
- Адрес: 100090, г. Ташкент, Яккасарайский район, ул. Кичик Бешёгоч 70-2
- Телефоны: +998 90 919-20-35, +998 90 188-69-12, +998 71 254-04-33
- Email: pir-management@mail.ru, k.prokudina83@gmail.com
- Сайт: www.prokar.uz
- Режим работы: Пн–Пт, 9:00–18:00

Услуги компании:
1. Обязательный аудит (для госпредприятий, банков, совместных предприятий и др.)
2. Налоговое консультирование и оптимизация налогообложения
3. Бухгалтерский аутсорсинг и финансовая отчётность
4. Юридическое сопровождение бизнеса
5. Консалтинг по государственным закупкам
6. Отчётность по МСФО и НСБУ
7. Регистрация и ликвидация бизнеса
8. Кадровый учёт и делопроизводство

Инструкции:
- ВАЖНО: отвечайте ПОЛНОСТЬЮ на том языке, на котором написал пользователь (русский или узбекский). Все метки, заголовки и пояснения — тоже на языке пользователя.
- Будьте профессиональными, краткими и полезными.
- Не добавляйте служебные пометки, инструкции или технические комментарии в текст ответа.
- Для конкретных юридических/налоговых вопросов рекомендуйте обратиться к специалистам компании.
- Если вопрос не относится к аудиту, бухгалтерии, налогам, праву или услугам компании — вежливо откажитесь и направьте к менеджеру.
- Если вопрос неясен, двусмысленен или вы не можете дать точный ответ — направьте к менеджеру, указав контакты СТРОГО в таком формате (каждый номер и email — на отдельной строке):

+998 90 919-20-35
+998 90 188-69-12
+998 71 254-04-33

pir-management@mail.ru
k.prokudina83@gmail.com"""


def _get_client_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    return (forwarded.split(',')[0].strip() if forwarded
            else request.META.get('REMOTE_ADDR', '')) or None


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


@require_POST
def ai_chat(request):
    message = request.POST.get('message', '').strip()
    raw_key = request.POST.get('s', '').strip()

    if not message:
        return JsonResponse({'error': 'empty'}, status=400)

    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key:
        return JsonResponse({'error': 'AI not configured'}, status=503)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
    except ImportError:
        return JsonResponse({'error': 'openai package not installed'}, status=503)

    # Resolve / create session
    session = None
    try:
        key = _uuid.UUID(raw_key)
        session, _ = AIChatSession.objects.get_or_create(
            session_key=key,
            defaults={
                'ip_address': _get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
            },
        )
    except (ValueError, TypeError):
        pass  # invalid UUID — proceed without persistence

    # Load history before saving new message
    history = []
    if session:
        recent = list(session.messages.order_by('-created_at')[:20])
        history = [{'role': m.role, 'content': m.content} for m in reversed(recent)]
        AIChatMessage.objects.create(session=session, role='user', content=message)

    def sse_stream():
        full = []
        try:
            stream = client.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {'role': 'system', 'content': _AI_SYSTEM_PROMPT},
                    *history,
                    {'role': 'user', 'content': message},
                ],
                stream=True,
                max_tokens=1200,
                temperature=0.7,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full.append(delta)
                    yield f'data: {json.dumps({"delta": delta})}\n\n'
        except Exception as exc:
            yield f'data: {json.dumps({"error": str(exc)})}\n\n'
        finally:
            if session and full:
                AIChatMessage.objects.create(
                    session=session, role='assistant', content=''.join(full),
                )
                AIChatSession.objects.filter(pk=session.pk).update(updated_at=timezone.now())
            yield 'data: [DONE]\n\n'

    resp = StreamingHttpResponse(sse_stream(), content_type='text/event-stream; charset=utf-8')
    resp['X-Accel-Buffering'] = 'no'
    resp['Cache-Control'] = 'no-cache'
    return resp


def ai_chat_history(request):
    raw_key = request.GET.get('s', '').strip()
    try:
        key = _uuid.UUID(raw_key)
        session = AIChatSession.objects.get(session_key=key)
    except (ValueError, TypeError, AIChatSession.DoesNotExist):
        return JsonResponse({'messages': []})

    msgs = list(session.messages.order_by('created_at').values('role', 'content', 'created_at'))
    for m in msgs:
        m['created_at'] = m['created_at'].isoformat()
    return JsonResponse({'messages': msgs})


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
