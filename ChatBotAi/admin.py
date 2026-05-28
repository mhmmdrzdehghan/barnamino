
from django.contrib import admin
from .models import Conversation, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ("role", "text", "created_at")
    ordering = ("created_at",)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_by",
        "message_count",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "created_at",
        "updated_at",
    )

    search_fields = (
        "created_by__username",
        "created_by__email",
    )

    inlines = [MessageInline]

    ordering = ("-created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("created_by")

    def message_count(self, obj):
        return obj.Messages.count()

    message_count.short_description = "Messages"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "conversation",
        "role",
        "short_text",
        "created_at",
    )

    list_filter = (
        "role",
        "created_at",
    )

    search_fields = (
        "text",
        "conversation__created_by__username",
    )

    autocomplete_fields = ("conversation",)

    ordering = ("-created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("conversation", "conversation__created_by")

    def short_text(self, obj):
        return obj.text[:80]

    short_text.short_description = "Message"



from django.contrib import admin
from .models import AiMentorReport


@admin.register(AiMentorReport)
class AiMentorReportAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'type',
        'created_at',
    )

    list_filter = (
        'type',
        'created_at',
    )

    search_fields = (
        'user__username',
        'user__email',
    )

    readonly_fields = (
        'created_at',
    )

    ordering = ('-created_at',)
