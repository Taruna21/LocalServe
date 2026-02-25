from rest_framework import serializers
from .models import ChatRoom, Message
from users.models import User


class MessageSerializer(serializers.ModelSerializer):
    sender_phone = serializers.CharField(source='sender.phone', read_only=True)
    sender_name  = serializers.CharField(source='sender.full_name', read_only=True)

    class Meta:
        model  = Message
        fields = ['id', 'content', 'sender_phone', 'sender_name', 'timestamp', 'is_read']


class ChatRoomSerializer(serializers.ModelSerializer):
    job_title      = serializers.CharField(source='job.title', read_only=True)
    seeker_phone   = serializers.CharField(source='seeker.phone', read_only=True)
    recruiter_phone = serializers.CharField(source='recruiter.phone', read_only=True)
    last_message   = serializers.SerializerMethodField()

    class Meta:
        model  = ChatRoom
        fields = ['id', 'job', 'job_title', 'seeker_phone', 'recruiter_phone', 'last_message', 'created_at']

    def get_last_message(self, obj):
        last = obj.messages.last()
        return last.content if last else None