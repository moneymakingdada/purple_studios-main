"""
Fire-and-forget SMS dispatch so a slow or failing SMS gateway never adds
latency to (or breaks) the API request that triggered it.
"""
import logging
import threading

from .sms import send_sms

logger = logging.getLogger("notifications.dispatch")


def send_sms_async(to: str, message: str) -> None:
    def _run():
        try:
            send_sms(to, message)
        except Exception:
            # send_sms already catches its own errors and returns False, but this
            # is a last-resort guard so a background thread can never crash silently
            # in a way that's invisible — always at least log it.
            logger.exception("Unexpected error sending SMS to %s", to)

    thread = threading.Thread(target=_run, daemon=True)
    thread.start()
