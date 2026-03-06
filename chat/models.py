from django.db import models
from users.models import User
from jobs.models import Job


class ChatRoom(models.Model):
    # job is now optional — allows direct DMs
    job       = models.ForeignKey(Job,  on_delete=models.CASCADE, related_name='chat_rooms', null=True, blank=True)
    seeker    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seeker_rooms')
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recruiter_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['seeker', 'recruiter']

    def other_user(self, user):
        return self.recruiter if user == self.seeker else self.seeker

    def __str__(self):
        return f"{self.seeker.phone} ↔ {self.recruiter.phone}"


class Message(models.Model):
    room      = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender    = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content   = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read   = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.phone}: {self.content[:50]}"
