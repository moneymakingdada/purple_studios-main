from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Session


@admin.register(Session)
class SessionAdmin(ModelAdmin):
    list_display = ("wa_phone", "customer", "status", "message_count", "last_message_at", "created_at")
    list_filter = ("status",)
    search_fields = ("wa_phone", "customer__email", "customer__first_name", "customer__last_name")
    readonly_fields = ("id", "created_at", "last_message_at", "messages_preview")
    fields = ("wa_phone", "customer", "status", "context", "messages_preview", "id", "created_at", "last_message_at")
    ordering = ("-last_message_at",)

    @admin.display(description="Messages")
    def message_count(self, obj):
        return len(obj.messages or [])

    @admin.display(description="Conversation")
    def messages_preview(self, obj):
        from django.utils.html import format_html

        if not obj.messages:
            return "No messages yet."
        lines = [f"[{m.get('role', '?')}] {m.get('content', '')}" for m in obj.messages[-20:]]
        return format_html("<pre style='white-space:pre-wrap;'>{}</pre>", "\n".join(lines))
