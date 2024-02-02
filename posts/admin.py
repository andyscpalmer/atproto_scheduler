from django.contrib import admin
from posts.models import Post, Config



class PostAdmin(admin.ModelAdmin):
    list_display = ['post_snippet', 'bluesky_username', 'is_draft', 'scheduled_post_time', 'posted_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        (
            None,
            {
                "classes": ["extrapretty"],
                "fields": ["text", "bluesky_username", "is_draft", "scheduled_post_time"]
            }
        ),
        (
            "Add links",
            {
                "classes": ["collapse", "extrapretty"],
                "fields": ["link_1", ("link_card_title", "link_card_description"), "link_2", "link_3", "link_4"]
            }
        ),
        (
            "Add images",
            {
                "classes": ["collapse", "extrapretty"],
                "fields": [("image_1", "alt_1"), ("image_2", "alt_2"), ("image_3", "alt_3"), ("image_4", "alt_4")]
            }
        ),
        (
            "Reset posted info",
            {
                "classes": ["collapse", "extrapretty"],
                "fields": ["posted_at", "cid", "uri"]
            }
        ),
    ]

class ConfigAdmin(admin.ModelAdmin):
    list_display = ['bluesky_username', 'interval_hours', 'interval_minutes', 'allow_posts']

admin.site.register(Post, PostAdmin)
admin.site.register(Config, ConfigAdmin)
