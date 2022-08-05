from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, UpdateView, ListView, DetailView, FormView

from .models import Meeting
from .utils import generate_agora_token
from .forms import CreateMeetingForm, UpdateMeetingForm, WaitingForm


class CreateMeetingView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Meeting
    form_class = CreateMeetingForm
    template_name = 'meeting/create.html'
    extra_context = {
        'title': 'Create Meeting'
    }
    success_url = reverse_lazy('meeting:list')
    success_message = "Meeting has created successfully"

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateMeetingView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Meeting
    form_class = UpdateMeetingForm
    pk_url_kwarg = "id"
    template_name = 'meeting/update.html'
    extra_context = {
        'title': 'Update Meeting'
    }
    success_url = reverse_lazy('meeting:list')
    success_message = "Meeting has updated successfully"


class UserMeetingListView(LoginRequiredMixin, ListView):
    model = Meeting
    template_name = 'meeting/list.html'
    extra_context = {
        'title': 'Meeting List'
    }
    context_object_name = "meetings"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user).order_by('-created')


class RoomView(LoginRequiredMixin, DetailView):
    model = Meeting
    context_object_name = 'room'
    slug_url_kwarg = 'channel_name'
    template_name = 'meeting/room.html'

    redirect_url = 'meeting:waiting'
    redirect_message = "The time hasn't come yet or it has already pass"

    extra_context = {
        'title': 'Meeting Room',
        'app_id': settings.AGORA_APP_ID,
    }

    def get_redirect_message(self):
        return self.redirect_message

    def get_redirect_url(self):
        return self.redirect_url

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()

        if not obj.is_timely_available():
            messages.error(self.request, self.get_redirect_message())
            return redirect(self.get_redirect_url())

        if request.user.is_authenticated and obj.user == request.user:
            request.session['uid'] = obj.uid
            request.session['token'] = obj.token
            request.session['name'] = request.user.get_full_name() or request.user.username
            return super().dispatch(request, *args, **kwargs)

        if 'token' in request.session:
            return super().dispatch(request, *args, **kwargs)

        request.session['end_at'] = obj.end_at.timestamp()
        request.session['channel_name'] = self.kwargs.get(self.slug_url_kwarg)
        return redirect(self.redirect_url)

    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.slug_url_kwarg)
        obj = get_object_or_404(self.model, **{self.slug_url_kwarg: slug})
        return obj


class WaitingView(LoginRequiredMixin, FormView):
    template_name = 'meeting/waiting.html'
    form_class = WaitingForm
    success_url = 'meeting:room'
    failed_message = "You don't have a room to be redirect to it"

    def get_failed_message(self):
        return self.failed_message

    def dispatch(self, request, *args, **kwargs):
        if 'channel_name' not in request.session:
            return PermissionDenied(self.get_failed_message())
        return super(WaitingView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.request.session['name'] = str(form.cleaned_data.get('name'))
        return super(WaitingView, self).form_valid(form)

    def get_success_url(self):
        channel_name = self.request.session.get('channel_name')
        expiration_time = self.request.session.get('end_at')
        token, uid = generate_agora_token(channel_name=channel_name, expiration_time=expiration_time)
        self.request.session.update({
            'uid': uid,
            'token': token
        })
        return reverse(self.success_url, args=[channel_name, ])
