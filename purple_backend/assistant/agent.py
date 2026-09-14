"""
The actual "agentic" part: a loop that sends the conversation + tool
definitions to Claude, executes whatever tools it asks for against our
booking system, feeds the results back, and repeats until Claude has a
final text reply for the customer.

Deliberately provider-shaped like notifications/sms.py: one function that
never raises out to the webhook view, always returns *some* string to send
back, and logs the real failure reason rather than surfacing it to WhatsApp.
"""
import json
import logging

import requests
from django.conf import settings

from .tools import TOOL_FUNCTIONS, TOOL_SCHEMAS, ToolError

logger = logging.getLogger("assistant.agent")

ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"
MAX_TOOL_ROUNDS = 5
REQUEST_TIMEOUT_SECONDS = 30

SYSTEM_PROMPT = """You are Purple's WhatsApp booking assistant for a beauty salon in Accra, Ghana \
(men's cuts, women's styling, lash extensions, nails & pedicure). You help customers browse \
services and stylists, check availability, book appointments, view their upcoming bookings, \
and cancel if needed.

Be warm, brief, and conversational — this is WhatsApp, not email. Use the tools rather than \
guessing prices, availability, or stylist names; only state facts a tool has actually returned. \
Prices are in GHS. Dates should be confirmed back to the customer in a friendly format (e.g. \
"Tuesday 16 September") even though tools take YYYY-MM-DD.

If this is a new customer (no name on file) and they're ready to book, ask for their name once, \
then call book_appointment with customer_name set — you don't need to ask again after that.

Never invent a booking_id, stylist, or time slot — only ones returned by a tool are real."""


def _history_to_anthropic_messages(session):
    """Session.messages is [{role, content, timestamp}, ...] — Anthropic just
    wants [{role, content}, ...] with content as a plain string per turn."""
    return [{"role": m["role"], "content": m["content"]} for m in session.messages]


def _call_claude(messages):
    if not settings.ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set — cannot run agent")
        return None

    headers = {
        "x-api-key": settings.ANTHROPIC_API_KEY,
        "anthropic-version": ANTHROPIC_API_VERSION,
        "content-type": "application/json",
    }
    body = {
        "model": settings.ANTHROPIC_MODEL,
        "max_tokens": 1024,
        "system": SYSTEM_PROMPT,
        "messages": messages,
        "tools": TOOL_SCHEMAS,
    }

    try:
        response = requests.post(ANTHROPIC_MESSAGES_URL, json=body, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        body_text = getattr(exc.response, "text", "") if getattr(exc, "response", None) else ""
        logger.error("Anthropic API call failed: %s %s", exc, body_text)
        return None


def _execute_tool(session, name: str, tool_input: dict) -> dict:
    func = TOOL_FUNCTIONS.get(name)
    if not func:
        return {"error": f"Unknown tool '{name}'"}
    try:
        return func(session, **tool_input)
    except ToolError as exc:
        return {"error": str(exc)}
    except Exception:
        logger.exception("Tool '%s' raised unexpectedly with input %s", name, tool_input)
        return {"error": "Something went wrong running that — try rephrasing or try again shortly."}


def run_agent(session) -> str:
    """
    Runs the tool-use loop for the session's current conversation and
    returns the reply text to send back over WhatsApp. Always returns a
    string — falls back to an apologetic message if the API isn't
    configured or fails outright, rather than raising into the webhook view.
    """
    messages = _history_to_anthropic_messages(session)

    for _ in range(MAX_TOOL_ROUNDS):
        result = _call_claude(messages)
        if result is None:
            return "Sorry, I'm having trouble connecting right now — please try again in a moment."

        stop_reason = result.get("stop_reason")
        content_blocks = result.get("content", [])

        if stop_reason != "tool_use":
            text_parts = [b["text"] for b in content_blocks if b.get("type") == "text"]
            return "\n".join(text_parts).strip() or "Sorry, I didn't quite catch that — could you rephrase?"

        # Assistant's tool-use turn goes back into history verbatim...
        messages.append({"role": "assistant", "content": content_blocks})

        # ...then one user turn carrying every tool_result for this round.
        tool_results = []
        for block in content_blocks:
            if block.get("type") != "tool_use":
                continue
            output = _execute_tool(session, block["name"], block.get("input", {}))
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block["id"],
                "content": json.dumps(output),
            })
        messages.append({"role": "user", "content": tool_results})

    return "That took a bit long to sort out — could you try asking again, maybe a bit more simply?"
