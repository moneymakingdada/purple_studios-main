"""
Callback functions referenced by the UNFOLD setting in settings.py.
Unfold calls these itself — nothing else needs to invoke them directly.
"""
import logging

logger = logging.getLogger("dashboard")


def dashboard_callback(request, context):
    """
    Unfold calls this on every admin homepage load and merges whatever we
    return into the template context, which our templates/admin/index.html
    override then renders. If analytics ever fails to compute (e.g. right
    after a fresh migrate with zero data), we fall back to an empty dict
    rather than letting a dashboard bug take down the whole admin homepage.
    """
    from .analytics import get_dashboard_stats

    try:
        context["analytics"] = get_dashboard_stats()
    except Exception:
        logger.exception("Failed to compute dashboard analytics")
        context["analytics"] = None
    return context


def environment_callback(request):
    """Small badge shown in the Unfold header — mirrors DJANGO_DEBUG so it's
    obvious at a glance whether you're looking at a dev or production instance."""
    from django.conf import settings

    if settings.DEBUG:
        return ["Development", "warning"]
    return ["Production", "success"]
