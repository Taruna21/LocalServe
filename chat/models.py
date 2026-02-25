from django.db import models
from users.models import User
from jobs.models import Job


class ChatRoom(models.Model):
    """
    A conversation between a seeker and recruiter about a specific job.
    Each unique seeker+recruiter+job combo gets one room.
    """
    job       = models.ForeignKey(Job,  on_delete=models.CASCADE, related_name='chat_rooms')
    seeker    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seeker_rooms')
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recruiter_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Only one room per seeker+recruiter+job combo
        unique_together = ['job', 'seeker', 'recruiter']

    def __str__(self):
        return f"Room: {self.seeker.phone} ↔ {self.recruiter.phone} | {self.job.title}"


class Message(models.Model):
    room      = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content   = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read   = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']  # oldest first

    def __str__(self):
        return f"{self.sender.phone}: {self.content[:50]}"