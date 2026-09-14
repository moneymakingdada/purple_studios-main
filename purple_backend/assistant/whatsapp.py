"""
Thin client for WhatsApp Cloud API — sending messages out and verifying the
webhook subscription. Mirrors the shape of notifications/sms.py: one function
per concern, never raises out to callers, logs failures instead.
"""
import logging

import requests
from django.conf import settings

logger = logging.getLogger("assistant.whatsapp")

GRAPH_API_VERSION = "v21.0"


def send_whatsapp_message(to: str, text: str) -> bool:
    """Send a plain text WhatsApp message. Returns True on success, False on any failure."""
    if not settings.WHATSAPP_ACCESS_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
        logger.warning("WhatsApp credentials not set — skipping send to %s. Message was: %s", to, text)
        return False

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    # WhatsApp wants the number without a leading '+' in this field.
    payload = {
        "messaging_product": "whatsapp",
        "to": to.lstrip("+"),
        "type": "text",
        "text": {"body": text},
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        logger.info("WhatsApp message sent to %s", to)
        return True
    except requests.RequestException as exc:
        body = getattr(exc.response, "text", "") if getattr(exc, "response", None) else ""
        logger.error("WhatsApp send to %s failed: %s %s", to, exc, body)
        return False


def verify_webhook_challenge(mode: str, token: str, challenge: str):
    """
    Implements Meta's webhook verification handshake: return the challenge
    string if mode/token check out, else None (caller responds 403).
    """
    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN and settings.WHATSAPP_VERIFY_TOKEN:
        return challenge
    return None


def extract_incoming_message(payload: dict):
    """
    Pulls (wa_phone, text, contact_name) out of a WhatsApp Cloud API webhook
    POST body. Returns None if this payload doesn't contain an actual text
    message (e.g. it's a delivery-status update, or an image/voice note).
    """
    try:
        entry = payload["entry"][0]
        change = entry["changes"][0]
        value = change["value"]
        messages = value.get("messages")
        if not messages:
            return None  # status update, not an incoming message

        message = messages[0]
        wa_phone = "+" + message["from"].lstrip("+")

        if message.get("type") != "text":
            return {"wa_phone": wa_phone, "text": None, "contact_name": None, "unsupported_type": message.get("type")}

        text = message["text"]["body"]
        contact_name = None
        contacts = value.get("contacts")
        if contacts:
            contact_name = contacts[0].get("profile", {}).get("name")

        return {"wa_phone": wa_phone, "text": text, "contact_name": contact_name, "unsupported_type": None}
    except (KeyError, IndexError, TypeError):
        return None
