from datetime import timedelta

from django.contrib import admin
from django.db import models
from django.utils import timezone

from posts.utils.constants import PUBLISH_STATUS_EMOJIS
from posts.utils.helper_functions import name_with_animal_emoji


class Config(models.Model):
    bluesky_username = models.CharField(max_length=100, primary_key=True, unique=True)
    app_password = models.CharField(max_length=50)
    interval = models.DurationField(default=timedelta(hours=24))

    allow_posts = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Bluesky User Configuration"
        verbose_name_plural = "Bluesky User Configurations"
        ordering = ["bluesky_username"]

    @admin.display(description="Publishing Status")
    def publishing_status(self) -> str:
        """Display whether a user's ability to publish is set to disabled or active

        Returns:
            str: Bluesky Username with an emoji for easier identification by eye
        """
        publishing_status = f"{PUBLISH_STATUS_EMOJIS['disabled']} Disabled"
        if self.allow_posts:
            publishing_status = f"{PUBLISH_STATUS_EMOJIS['enabled']} Active"
        return publishing_status

    @admin.display(description="Bluesky User")
    def name_with_emoji(self) -> str:
        """Generate an emoji derived arbitrarily from the characters in the username.

        Returns:
            str: Bluesky Username with an emoji for easier identification by eye
        """
        return name_with_animal_emoji(self.bluesky_username)

    def __str__(self):
        return self.bluesky_username


class Post(models.Model):

    text = models.TextField(max_length=300)
    bluesky_username = models.ForeignKey(
        Config, on_delete=models.CASCADE, null=True, blank=True
    )
    link_1 = models.CharField(max_length=300, null=True, blank=True)
    link_card_title = models.CharField(max_length=100, null=True, blank=True)
    link_card_description = models.CharField(max_length=100, null=True, blank=True)
    link_2 = models.CharField(max_length=300, null=True, blank=True)
    link_3 = models.CharField(max_length=300, null=True, blank=True)
    link_4 = models.CharField(max_length=300, null=True, blank=True)
    image_1 = models.CharField(max_length=200, null=True, blank=True)
    image_2 = models.CharField(max_length=200, null=True, blank=True)
    image_3 = models.CharField(max_length=200, null=True, blank=True)
    image_4 = models.CharField(max_length=200, null=True, blank=True)
    alt_1 = models.TextField(max_length=500, null=True, blank=True)
    alt_2 = models.TextField(max_length=500, null=True, blank=True)
    alt_3 = models.TextField(max_length=500, null=True, blank=True)
    alt_4 = models.TextField(max_length=500, null=True, blank=True)
    is_draft = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    cid = models.CharField(max_length=300, null=True, blank=True)
    uri = models.CharField(max_length=300, null=True, blank=True)
    scheduled_post_time = models.DateTimeField(null=True, blank=True)
    error = models.CharField(max_length=2000, null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    @admin.display(description="Post snippet")
    def post_snippet(self) -> str:
        return self.text[:100]

    @admin.display(description="Status")
    def post_status(self) -> str:
        is_published = True if self.posted_at or (self.cid and self.uri) else False
        if self.is_draft and self.error:
            return "❌ Error"
        elif self.is_draft:
            return "📝 Draft"
        elif is_published:
            return "✅ Published"
        else:
            schedule_time_formatted = "awaiting time assignment..."
            if self.scheduled_post_time:
                timezone_info = timezone.get_current_timezone()
                schedule_time_formatted = self.scheduled_post_time.astimezone(
                    tz=timezone_info
                ).strftime("%b. %d, %Y, %I:%M %p")
            return f"⏳ Scheduled - {schedule_time_formatted}"

    @admin.display(description="Bluesky User")
    def name_with_emoji(self) -> str:
        """Generate an emoji derived arbitrarily from the characters in the username.

        There is also an emoji for whether posts are enabled.

        Returns:
            str: Bluesky Username with an emoji for easier identification by eye
        """
        user_config = Config.objects.filter(
            bluesky_username=self.bluesky_username
        ).first()
        if user_config:
            publish_flag = PUBLISH_STATUS_EMOJIS["disabled"]
            if user_config.allow_posts:
                publish_flag = PUBLISH_STATUS_EMOJIS["enabled"]
            return f"{name_with_animal_emoji(self.bluesky_username)} {publish_flag}"
        else:
            return "❓ unassigned ❓"

    def __str__(self):
        return f"{self.id}_{self.text[:50]}"
