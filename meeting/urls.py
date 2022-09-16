from django.urls import path
from .views import CreateMeetingView, UpdateMeetingView, UserMeetingListView, RoomView, CreateOrGetMeetingMember

app_name = 'meeting'


urlpatterns = [
    path('create/', CreateMeetingView.as_view(), name='create'),
    path('update/<int:id>', UpdateMeetingView.as_view(), name='update'),
    path('list/', UserMeetingListView.as_view(), name='list'),

    path('room/<str:channel_name>', RoomView.as_view(), name='room'),

    path('member/get/<int:uid>/<str:channel_name>/', CreateOrGetMeetingMember.as_view(), name='member_get'),
    path('member/create/', CreateOrGetMeetingMember.as_view(), name='member_create'),
]
