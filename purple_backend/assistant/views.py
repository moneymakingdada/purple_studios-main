import json
import logging

from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .agent import run_agent
from .models import Session
from .whatsapp import extract_incoming_message, send_whatsapp_message, verify_webhook_challenge

logger = logging.getLogger("assistant.views")


@method_decorator(csrf_exempt, name="dispatch")
class WhatsAppWebhookView(View):
    """
    GET  — Meta's one-time webhook verification handshake.
    POST — actual incoming messages. Always returns 200 quickly (Meta
    retries/backs off aggressively on non-200s) even when we can't fully
    process a message — the failure is logged, not surfaced as an HTTP error.
    """

    def get(self, request):
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        result = verify_webhook_challenge(mode, token, challenge)
        if result is not None:
            return HttpResponse(result)
        return HttpResponseForbidden("Verification failed")

    def post(self, request):
        try:
            payload = json.loads(request.body.decode())
        except (ValueError, UnicodeDecodeError):
            logger.warning("Webhook received non-JSON body")
            return JsonResponse({"status": "ignored"}, status=200)

        parsed = extract_incoming_message(payload)
        if parsed is None:
            return JsonResponse({"status": "ignored"}, status=200)  # e.g. a delivery-status callback

        if parsed["text"] is None:
            # An image/voice-note/etc rather than text — reply with a nudge, don't crash.
            session, _ = Session.objects.get_or_create(wa_phone=parsed["wa_phone"])
            send_whatsapp_message(
                parsed["wa_phone"],
                "I can only read text messages right now — could you type that instead?",
            )
            return JsonResponse({"status": "ok"}, status=200)

        self._handle_text_message(parsed["wa_phone"], parsed["text"], parsed.get("contact_name"))
        return JsonResponse({"status": "ok"}, status=200)

    def _handle_text_message(self, wa_phone: str, text: str, contact_name: str | None):
        session, _ = Session.objects.get_or_create(wa_phone=wa_phone)
        session.link_customer_if_unset()

        if contact_name and session.customer and not session.customer.first_name:
            first, _, last = contact_name.partition(" ")
            session.customer.first_name = first
            session.customer.last_name = last
            session.customer.save(update_fields=["first_name", "last_name"])

        session.add_message("user", text)
        session.save()

        try:
            reply = run_agent(session)
        except Exception:
            logger.exception("Agent run failed for session %s", session.id)
            reply = "Sorry, something went wrong on my end — please try again shortly."

        session.add_message("assistant", reply)
        session.save()

        send_whatsapp_message(wa_phone, reply)
