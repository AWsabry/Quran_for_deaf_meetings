from django.urls import path
from .views import CreateMeetingView, UpdateMeetingView, UserMeetingListView, RoomView, WaitingView

app_name = 'meeting'


urlpatterns = [
    path('create/', CreateMeetingView.as_view(), name='create'),
    path('update/<int:id>', UpdateMeetingView.as_view(), name='update'),
    path('list/', UserMeetingListView.as_view(), name='list'),

    path('room/<str:channel_name>', RoomView.as_view(), name='room'),
    path('waiting/', WaitingView.as_view(), name='waiting'),
]
