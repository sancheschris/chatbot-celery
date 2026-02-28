# from openai import OpenAI
import os

from google import genai
from django.db import models

from core.tasks import handle_ai_request_job

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

    def _queue_job(self):
        """Add job to queue"""
        handle_ai_request_job.delay(self.id)

    def handle(self):
        """Handle request"""
        self.status = self.RUNNING
        self.save()
        client = genai.Client(api_key=os.environ.get("GENAI_API_KEY"))
        try:
            completion = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=self.messages
            )
            self.response = completion.to_dict()
            self.status = self.COMPLETE
        except Exception as e:
            error_message = str(e)
            print(f"Error processing AI request {self.id}: {error_message}")
            self.status = self.FAILED
        
        self.save()

    def save(self, **kwargs):
        is_new = self._state.adding
        super().save(**kwargs)
        if is_new:
            self._queue_job()