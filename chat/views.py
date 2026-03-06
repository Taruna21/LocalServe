from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import ChatRoom, Message
from users.models import User


@login_required
def chat_list(request):
    user = request.user
    rooms = ChatRoom.objects.filter(
        Q(seeker=user) | Q(recruiter=user)
    ).prefetch_related('messages')

    # Attach last message and unread count to each room
    for room in rooms:
        room.last_msg    = room.messages.last()
        room.other       = room.other_user(user)
        room.unread      = room.messages.filter(is_read=False).exclude(sender=user).count()

    return render(request, 'chat/chat_list.html', {'rooms': rooms})


@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    user = request.user

    # Only participants can view
    if user not in [room.seeker, room.recruiter]:
        messages.error(request, 'You are not part of this conversation.')
        return redirect('chat_list')

    # Mark messages as read
    room.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            Message.objects.create(room=room, sender=user, content=content)
        return redirect('chat_room', room_id=room.id)

    msgs      = room.messages.all()
    other     = room.other_user(user)
    return render(request, 'chat/chat_room.html', {
        'room':  room,
        'msgs':  msgs,
        'other': other,
    })


@login_required
def start_chat(request, user_id):
    """Start or open a DM with any user."""
    other_user = get_object_or_404(User, id=user_id)
    current    = request.user

    if other_user == current:
        return redirect('chat_list')

    # Figure out who is seeker and who is recruiter
    if current.role == 'seeker':
        seeker, recruiter = current, other_user
    else:
        seeker, recruiter = other_user, current

    room, _ = ChatRoom.objects.get_or_create(
        seeker=seeker,
        recruiter=recruiter,
    )
    return redirect('chat_room', room_id=room.id)
