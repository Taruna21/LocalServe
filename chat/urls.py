from django.urls import path
from . import views

urlpatterns = [
    path('room/',                          views.GetOrCreateRoomView.as_view(), name='get-or-create-room'),
    path('rooms/',                         views.MyRoomsView.as_view(),         name='my-rooms'),
    path('rooms/<int:room_id>/messages/',  views.RoomMessagesView.as_view(),    name='room-messages'),
]