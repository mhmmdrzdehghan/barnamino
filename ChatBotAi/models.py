from django.db import models
from Account.models import User


class Role(models.TextChoices):
    USER = "user",
    AI = "assistant"


class Type(models.TextChoices):
    REPORT = "report",
    MENTOR = "mentor"


class Conversation(models.Model):
    created_by = models.ForeignKey(User , on_delete=models.CASCADE , related_name='conversation')

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)



class Message(models.Model):
    text         = models.TextField()
    role         = models.CharField(max_length=50 , choices=Role.choices)
    conversation = models.ForeignKey(Conversation, related_name='Messages', on_delete=models.CASCADE)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)


class AiMentorReport(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    type       = models.CharField(max_length=50 , choices=Type.choices)
    result     = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

