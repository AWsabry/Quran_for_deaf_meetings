from django.db import models
from django.urls import reverse
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.backends import get_user_model

from .utils import random_str_shuffle, generate_random_str, generate_agora_token

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

    def get_meeting_url(self, request):
        protocol = request.scheme + "://"
        domain = request.META['HTTP_HOST']
        view_oath = reverse('meeting:room', args=[self.channel_name, ])
        return protocol + domain + view_oath


@receiver(post_save, sender=Meeting)
def create_meeting_channel(sender, instance, created, **kwargs) -> None:
    if not created:
        return
    title = instance.title or generate_random_str(10)
    description = instance.description or generate_random_str(10)
    channel_name = random_str_shuffle(title + description, 20)
    instance.channel_name = channel_name
    try:
        token, uid = generate_agora_token(channel_name=channel_name, expiration_time=instance.end_at.timestamp())
        instance.token = token
        instance.uid = uid
    except Exception as e:
        print(e)
    finally:
        instance.save()
