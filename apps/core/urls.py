from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('feedback/', views.feedback_submit, name='feedback_submit'),
    path('staff/<slug:slug>/', views.staff_detail, name='staff_detail'),
    path('api/ai-chat/', views.ai_chat, name='ai_chat'),
    path('api/ai-chat/history/', views.ai_chat_history, name='ai_chat_history'),
]
