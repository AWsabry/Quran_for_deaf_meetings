from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, UpdateView
from django.contrib.auth import login
from django.contrib.auth.backends import get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin

from .forms import RegistrationForm


User = get_user_model()
URL_REDIRECT = 'home'


class LogInView(SuccessMessageMixin, LoginView):
    template_name = 'accounts/auth/login.html'
    success_url = reverse_lazy(URL_REDIRECT)
    redirect_authenticated_user = True
    success_message = 'Logged in successfully'


class RegistrationView(SuccessMessageMixin, CreateView):
    form_class = RegistrationForm
    template_name = 'accounts/auth/register.html'
    success_message = 'Registration has been completed successfully'
    success_url = reverse_lazy(URL_REDIRECT)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return HttpResponseRedirect(self.success_url)


class LogOutView(SuccessMessageMixin, LogoutView):
    template_name = 'accounts/auth/logout.html'
    success_message = 'Logged out successfully '
    success_url = reverse_lazy(URL_REDIRECT)
