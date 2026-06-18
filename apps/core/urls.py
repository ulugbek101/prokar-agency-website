from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('feedback/', views.feedback_submit, name='feedback_submit'),
    path('staff/<slug:slug>/', views.staff_detail, name='staff_detail'),
]
