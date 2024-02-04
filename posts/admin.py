from django.contrib import admin
from posts.models import Post, Config


@admin.action(
    description="Set As Draft",
)
def set_draft(modeladmin, request, queryset):
    queryset.update(is_draft=True)


@admin.action(
    description="Set To Publish",
)
def set_publish(modeladmin, request, queryset):
    queryset.update(is_draft=False)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = [
        "post_snippet",
        "name_with_emoji",
        "post_status",
    ]
    readonly_fields = ["error", "created_at", "updated_at"]
    fieldsets = [
        (
            None,
            {
                "classes": ["extrapretty"],
                "fields": [
                    "text",
                    "bluesky_username",
                    "is_draft",
                    "scheduled_post_time",
                ],
            },
        ),
        (
            "Add links",
            {
                "classes": ["collapse", "extrapretty"],
                "fields": [
                    ("link_1", "link_card_title", "link_card_description"),
                    "link_2",
                    "link_3",
                    "link_4",
                ],
            },
        ),
        (
            "Add images",
            {
                "classes": ["collapse", "extrapretty"],
                "fields": [
                    ("image_1", "alt_1"),
                    ("image_2", "alt_2"),
                    ("image_3", "alt_3"),
                    ("image_4", "alt_4"),
                ],
            },
        ),
        (
            "Reset posted info",
            {
                "classes": ["collapse", "extrapretty"],
                "fields": ["posted_at", "cid", "uri"],
            },
        ),
        (
            "Metadata",
            {
                "classes": ["collapse", "extrapretty"],
                "fields": ["error", "created_at", "updated_at"],
            },
        ),
    ]
    actions = [set_draft, set_publish]


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = [
        "name_with_emoji",
        "interval",
        "publishing_status",
    ]
