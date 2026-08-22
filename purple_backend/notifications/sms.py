"""
Thin SMS-sending layer. Default provider is Arkesel (a Ghana-based SMS
gateway that handles local +233 numbers well and supports custom sender IDs).

Swapping providers later just means adding a new branch in send_sms() —
nothing calling send_sms() needs to change.
"""
import logging

import requests
from django.conf import settings

from .phone_utils import normalize_ghana_phone

logger = logging.getLogger("notifications.sms")

ARKESEL_SEND_URL = "https://sms.arkesel.com/api/v2/sms/send"
REQUEST_TIMEOUT_SECONDS = 15  # Arkesel can be slower than a quick curl test under real load
MAX_ATTEMPTS = 2  # one retry on timeout/connection errors only — not on rejections


def send_sms(to: str, message: str) -> bool:
    """
    Send an SMS. Returns True on success, False on any failure — never raises,
    so a notification problem can never break the booking flow that triggered it.
    """
    if not settings.SMS_ENABLED:
        logger.info("SMS disabled (SMS_ENABLED=False) — skipping send to %s", to)
        return False

    if not to:
        logger.warning("send_sms called with no phone number — skipping")
        return False

    normalized = normalize_ghana_phone(to)
    if not normalized:
        logger.error("'%s' doesn't look like a valid Ghanaian phone number — skipping send", to)
        return False

    if normalized != to:
        logger.info("Normalized phone %s -> %s before sending", to, normalized)

    if settings.SMS_PROVIDER == "arkesel":
        return _send_via_arkesel(normalized, message)

    logger.error("Unknown SMS_PROVIDER '%s' — message not sent", settings.SMS_PROVIDER)
    return False


def _send_via_arkesel(to: str, message: str) -> bool:
    if not settings.ARKESEL_API_KEY:
        logger.warning("ARKESEL_API_KEY not set — skipping SMS to %s. Message was: %s", to, message)
        return False

    payload = {
        "sender": settings.ARKESEL_SENDER_ID,
        "message": message,
        "recipients": [to],
    }
    headers = {
        "api-key": settings.ARKESEL_API_KEY,
        "Content-Type": "application/json",
    }

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.post(
                ARKESEL_SEND_URL, json=payload, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "success" or data.get("code") == "ok":
                logger.info("SMS sent to %s", to)
                return True
            logger.error("Arkesel rejected SMS to %s: %s", to, data)
            return False  # a clean rejection response — retrying won't help, don't retry
        except (requests.Timeout, requests.ConnectionError) as exc:
            if attempt < MAX_ATTEMPTS:
                logger.warning("SMS send to %s timed out/failed to connect (attempt %d/%d), retrying: %s",
                                to, attempt, MAX_ATTEMPTS, exc)
                continue
            logger.error("SMS send to %s failed after %d attempts: %s", to, MAX_ATTEMPTS, exc)
            return False
        except requests.RequestException as exc:
            logger.error("SMS send to %s failed: %s", to, exc)
            return False

    return False
