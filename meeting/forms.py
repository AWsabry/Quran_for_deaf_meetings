from django import forms
from django.contrib.admin import widgets

from .models import Meeting


class CreateMeetingForm(forms.ModelForm):

    class Meta:
        model = Meeting
        fields = [
            'user', 'status', 'title', 'description', 'start_at', 'end_at'
        ]
        widgets = {
            'user': forms.HiddenInput(),
            'status': forms.HiddenInput(),
            'start_at': widgets.AdminSplitDateTime(),
            'end_at': widgets.AdminSplitDateTime()
        }


class UpdateMeetingForm(forms.ModelForm):

    class Meta:
        model = Meeting
        fields = [
           'status', 'title', 'description', 'start_at', 'end_at'
        ]


class WaitingForm(forms.Form):
    name = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))
