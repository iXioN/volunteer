from django.urls import path
from django.contrib.auth.views import LoginView

from . import views

urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name="login"),
    path('', views.index, name='summary'),
]
