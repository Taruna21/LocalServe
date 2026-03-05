from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from users.models import User
from jobs.models import Job

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ChatRoom


@login_required
def chat_list(request):
    rooms = ChatRoom.objects.filter(seeker=request.user) | \
            ChatRoom.objects.filter(recruiter=request.user)
    return render(request, 'chat/chat_list.html', {'rooms': rooms})


class GetOrCreateRoomView(APIView):
    """
    POST /api/chat/room/
    Seeker starts a chat with recruiter about a job.
    Creates room if doesn't exist, returns existing if it does.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        job_id       = request.data.get('job_id')
        recruiter_id = request.data.get('recruiter_id')

        try:
            job       = Job.objects.get(id=job_id)
            recruiter = User.objects.get(id=recruiter_id)
        except (Job.DoesNotExist, User.DoesNotExist):
            return Response({'error': 'Job or recruiter not found'}, status=404)

        room, created = ChatRoom.objects.get_or_create(
            job       = job,
            seeker    = request.user,
            recruiter = recruiter,
        )

        return Response({
            'room_id': room.id,
            'created': created,
            **ChatRoomSerializer(room).data
        })


class MyRoomsView(generics.ListAPIView):
    """
    GET /api/chat/rooms/
    Returns all chat rooms for logged in user.
    """
    serializer_class   = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return ChatRoom.objects.filter(
            seeker=user
        ) | ChatRoom.objects.filter(
            recruiter=user
        )


class RoomMessagesView(generics.ListAPIView):
    """
    GET /api/chat/rooms/<room_id>/messages/
    Returns message history for a room.
    """
    serializer_class   = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(room_id=self.kwargs['room_id'])