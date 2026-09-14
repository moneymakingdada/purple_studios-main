import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Session(models.Model):
    """
    One ongoing WhatsApp conversation with a single phone number. Designed for
    an agentic (LLM-driven) bot rather than a rigid step-by-step state machine:
    `messages` is the conversation history fed back to the model as context on
    every turn, and `context` is scratch/working memory the agent reads and
    writes as it builds up a booking (or looks up availability, etc.) across
    multiple messages — e.g. {"service_id": "...", "stylist_id": "...",
    "date": "2026-09-10"} while the customer is still deciding on a time.

    One Session per phone number (see unique=True on wa_phone) — rather than
    creating a new row per conversation, we keep a single evolving record and
    reset `context`/`status` when a booking flow completes or the customer
    starts something new. This keeps "resume where we left off" trivial: the
    bot just loads the Session for the incoming phone number.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"           # mid-conversation, expecting a reply
        IDLE = "idle", "Idle"                 # no recent activity, but not done/expired
        COMPLETED = "completed", "Completed"  # last flow (e.g. a booking) finished successfully
        EXPIRED = "expired", "Expired"        # gone stale; next message should start fresh

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    wa_phone = models.CharField(
        max_length=20, unique=True, db_index=True,
        help_text="WhatsApp phone number, normalized to international format e.g. +233241234567",
    )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="whatsapp_sessions",
        help_text="Linked customer account, if this phone number matches a registered user",
    )

    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    messages = models.JSONField(
        default=list, blank=True,
        help_text="Conversation history: list of {role, content, timestamp}, oldest first",
    )
    context = models.JSONField(
        default=dict, blank=True,
        help_text="Agent's working memory for the in-progress task, e.g. draft booking fields",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-last_message_at"]

    def __str__(self):
        who = self.customer.get_full_name() if self.customer else self.wa_phone
        return f"WhatsApp session — {who} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Normalize on every save so lookups by phone number are always
        # consistent, regardless of the format WhatsApp/the webhook sent in.
        from notifications.phone_utils import normalize_ghana_phone

        normalized = normalize_ghana_phone(self.wa_phone)
        if normalized:
            self.wa_phone = normalized
        super().save(*args, **kwargs)

    def add_message(self, role: str, content: str):
        """Append one turn to the conversation history and mark the session active/fresh."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": timezone.now().isoformat(),
        })
        self.status = self.Status.ACTIVE
        self.last_message_at = timezone.now()

    def link_customer_if_unset(self):
        """
        Best-effort match to an existing customer account by phone number.
        Safe to call repeatedly — a no-op once `customer` is already set, and
        never raises if no match is found.
        """
        if self.customer_id:
            return

        from accounts.models import User

        match = User.objects.filter(phone=self.wa_phone, role=User.Role.CUSTOMER).first()
        if match:
            self.customer = match
