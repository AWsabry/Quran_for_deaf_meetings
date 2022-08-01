import os
import binascii
from datetime import timedelta

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.utils.html import format_html
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.backends import get_user_model

from .utils import generate_agora_token


User = get_user_model()


STATUS = (
    ('coming', 'Coming'),
    ('progress', 'Progress'),
    ('finished', 'Finished'),
    ('cancelled', 'Canceled'),
)


class Meeting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(choices=STATUS, default='coming', max_length=20)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    channel_name = models.CharField(null=True, blank=True, unique=True, max_length=100)

    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    token = models.CharField(max_length=150, null=True, blank=True)
    uid = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

    def get_meeting_url(self, request):
        protocol = request.scheme + "://"
        domain = request.META['HTTP_HOST']
        view_oath = reverse('meeting:room', args=[self.channel_name, ])
        return protocol + domain + view_oath

    def get_meeting_link(self, request):
        if self.is_timely_available():
            link = self.get_meeting_url(request)
            return format_html('<a href="{}">{}</a>', link, 'GO Room')
        return "--"

    @staticmethod
    def generate_key():
        return binascii.hexlify(os.urandom(20)).decode()

    def is_timely_available(self):
        current = timezone.now()
        start_time = self.start_at - timedelta(minutes=15)
        end_time = self.end_at + timedelta(seconds=settings.AGORA_INCREASE_TIME)
        return start_time <= current <= end_time


@receiver(post_save, sender=Meeting)
def create_meeting_channel(sender, instance, created, **kwargs) -> None:
    if not created:
        return

    channel_name = sender.generate_key()
    instance.channel_name = channel_name
    try:
        token, uid = generate_agora_token(channel_name=channel_name, expiration_time=instance.end_at.timestamp())
        instance.token = token
        instance.uid = uid
    except Exception as e:
        print(e)
    finally:
        instance.save()
