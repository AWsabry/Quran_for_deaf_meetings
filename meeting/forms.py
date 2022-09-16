from django import forms
from django.contrib.admin import widgets

from .models import Meeting, MeetingMember


class CreateMeetingForm(forms.ModelForm):
    start_at = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime(), required=True)
    end_at = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime(), required=True)

    class Meta:
        model = Meeting
        fields = [
           'status', 'title', 'description', 'start_at', 'end_at'
        ]


class UpdateMeetingForm(forms.ModelForm):
    start_at = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime(), required=True)
    end_at = forms.SplitDateTimeField(widget=widgets.AdminSplitDateTime(), required=True)

    class Meta:
        model = Meeting
        fields = [
           'status', 'title', 'description', 'start_at', 'end_at'
        ]


class WaitingForm(forms.Form):
    name = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))


class CreateMeetingMember(forms.Form):
    user = forms.IntegerField(required=True)
    meeting = forms.IntegerField(required=True)
