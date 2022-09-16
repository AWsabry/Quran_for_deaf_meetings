from django.conf import settings
from django.http.response import JsonResponse
from django.urls import reverse, reverse_lazy
from django.urls.exceptions import NoReverseMatch
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, CreateView, UpdateView, ListView, DetailView, FormView
from django.contrib.auth.backends import get_user_model
from .utils import generate_agora_token
from .models import Meeting, MeetingMember
from .forms import CreateMeetingForm, UpdateMeetingForm, WaitingForm, CreateMeetingMember


User = get_user_model()


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
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        slug = self.kwargs.get(self.slug_url_kwarg)
        obj = get_object_or_404(self.model, **{self.slug_url_kwarg: slug})
        return obj


@method_decorator(csrf_exempt, name='dispatch')
class CreateOrGetMeetingMember(View):
    pk_field = "uid"
    pk_url_kwarg = "uid"
    slug_field = "meeting__channel_name"
    slug_url_kwarg = "channel_name"
    model = MeetingMember
    response_class = JsonResponse
    form_class = CreateMeetingMember
    http_method_names = ("get", "post")

    def render_to_response(self, context, **response_kwargs):
        """Render the response class."""
        return self.response_class(data=context, **response_kwargs)

    def get_object(self):
        """Get object or raise 404 error."""
        obj = get_object_or_404(
            self.model,
            **{
                self.pk_field: self.kwargs.get(self.pk_url_kwarg),
                self.slug_field: self.kwargs.get(self.slug_url_kwarg)
            }
        )
        return obj.as_dict()

    def get(self, request, uid=None, channel_name=None, *args, **kwargs):
        """Get object model"""
        if uid is None or channel_name is None:
            raise NoReverseMatch(f"URL missing one attribute ({self.url_kwarg})")
        context = {'data': self.get_object()}
        return self.render_to_response(context, **kwargs)

    def get_form_class(self):
        """Return the form class to use."""
        return self.form_class

    def post(self, request, *args, **kwargs):
        """Create object model."""
        Form = self.get_form_class()
        form = Form(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            data["meeting"] = get_object_or_404(Meeting, id=data.pop("meeting"))
            data["user"] = get_object_or_404(User, id=data.pop("user"))
            instance, created = self.model.objects.get_or_create(**data)
            context = {"data":  instance.as_dict()}
            kwargs.update({"status": 201 if created else 200})
            return self.render_to_response(context, **kwargs)

        context = {"errors": {f: e.get_json_data() for f, e in form.errors.items()}}
        kwargs.update({"status": 400})
        return self.render_to_response(context, **kwargs)
