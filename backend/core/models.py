from django.db import models

# Create your models here.
class AiChatSession(models.Model):
    """Model representing a chat session with the AI."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AiRequest(models.Model):
    """Model representing a request made to the AI."""

    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETE = 'complete'
    FAILED = 'failed'
    STATUS_OPTIONS = (
        (PENDING, 'Pending'),
        (RUNNING, 'Running'),
        (COMPLETE, 'Complete'),
        (FAILED, 'Failed'),
    )
    status = models.CharField(choices=STATUS_OPTIONS, default=PENDING)
    session = models.ForeignKey(
        AiChatSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    messages = models.JSONField()
    response = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)