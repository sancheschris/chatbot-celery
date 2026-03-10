# from openai import OpenAI
import os

from google import genai
from django.db import models

from core.tasks import handle_ai_request_job
from core.adapters.gemini_adapter import GeminiMessageAdapter

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
            contents, config = GeminiMessageAdapter.build(self.messages)
            
            completion = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=config
            )
            raw_response = completion.model_dump()
            text = self.extract_gemini_text(raw_response)

            print("GEMINI RAW RESPONSE:", raw_response)
            print("EXTRACTED TEXT:", text)

            self.response = {
                "text": text,
                "raw": raw_response,
            }
            self.status = self.COMPLETE
            
        except Exception as e:
            print(f"Error processing AI request {self.id}: {e}")
            self.response = {"error": str(e)}
            self.status = self.FAILED
        
        self.save(update_fields=["status", "response", "updated_at"])

    def save(self, **kwargs):
        is_new = self._state.adding
        super().save(**kwargs)
        if is_new:
            self._queue_job()

    def extract_gemini_text(self, raw_response: dict) -> str | None:
        candidates = raw_response.get("candidates") or []
        if not candidates:
            return None

        first_candidate = candidates[0] or {}
        content = first_candidate.get("content") or {}
        parts = content.get("parts") or []

        texts = []
        for part in parts:
            if isinstance(part, dict) and part.get("text"):
                texts.append(part["text"])

        result = "\n".join(texts).strip()
        return result or None