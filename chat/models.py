from django.db import models
import uuid

class User(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.uuid)

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    name = models.CharField(max_length=255, default='New Chat')
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"{self.name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

class ChatMessage(models.Model):
    session = models.ForeignKey("ChatSession", on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.session.name} - {self.timestamp.strftime("%Y-%m-%d %H:%M:%S")}'
