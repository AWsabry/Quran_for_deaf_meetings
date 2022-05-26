from django.urls import path

from .views import (RegistrationView, LogInView, LogOutView)


app_name = 'accounts'


urlpatterns = [
    path('login/', LogInView.as_view(), name='login'),
    path('logout/', LogOutView.as_view(), name='logout'),
    path('register/', RegistrationView.as_view(), name='register')
]
