from django.urls import path
from .views import CreateMeetingView, UpdateMeetingView, RoomView, WaitingView

app_name = 'meeting'


urlpatterns = [
    path('create/', CreateMeetingView.as_view(), name='create'),
    path('update/', UpdateMeetingView.as_view(), name='update'),

    path('room/<str:channel_name>', RoomView.as_view(), name='room'),
    path('waiting/', WaitingView.as_view(), name='waiting'),
]
