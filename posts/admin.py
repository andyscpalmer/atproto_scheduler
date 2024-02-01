from django.contrib import admin
from posts.models import Post, Config


class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'is_draft', 'scheduled_post_time', 'posted_at']

class ConfigAdmin(admin.ModelAdmin):
    list_display = ['bluesky_username', 'interval_hours', 'interval_minutes', 'allow_posts']

admin.site.register(Post, PostAdmin)
admin.site.register(Config, ConfigAdmin)
