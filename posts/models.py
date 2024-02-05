from datetime import timedelta

from django.contrib import admin
from django.db import models

from posts.utils.constants import PUBLISH_STATUS_EMOJIS, DETAIL_EMOJIS
from posts.utils.helper_functions import get_name_emoji, get_name_with_animal_emoji
from schedule_client.utils.data_models import PostObject


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
        return get_name_with_animal_emoji(self.bluesky_username)

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
    post_status = models.CharField(max_length=100, null=True, blank=True)
    reply_to = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    @admin.display(description="Post snippet")
    def post_snippet(self) -> str:
        return self.text[:100]

    def save(self, *args, **kwargs):
        is_published = True if self.posted_at or (self.cid and self.uri) else False
        if self.is_draft and self.error:
            self.post_status = "❌ Error"
        elif self.is_draft:
            self.post_status = "📝 Draft"
        elif is_published:
            self.post_status = "✅ Published"
        else:
            self.post_status = f"⏳ Scheduled"
        super(Post, self).save(*args, **kwargs)

    def reply_to_int(self) -> bool:
        if self.reply_to:
            return self.reply_to.id
        else:
            return 0

    def links(self) -> list[str]:
        links_raw = [self.link_1, self.link_2, self.link_3, self.link_4]
        return [link for link in links_raw if link]

    def images_raw(self) -> list[str]:
        images_raw = [self.image_1, self.image_2, self.image_3, self.image_4]
        return images_raw

    def alt_texts_raw(self) -> list[str]:
        return [self.alt_1, self.alt_2, self.alt_3, self.alt_4]

    def image_urls_with_alts(self) -> list[dict]:
        images = [image for image in self.images_raw() if image]
        image_urls_with_alts = [
            {"image": images[i], "alt_text": self.alt_texts_raw()[i]}
            for i in range(len(images))
        ]
        return image_urls_with_alts

    def is_link_card(self) -> bool:
        single_link = len(self.links()) == 1
        has_card_title = self.link_card_title not in ("", None)
        has_card_description = self.link_card_description not in ("", None)
        return single_link and has_card_title and has_card_description

    def post_object(self) -> PostObject:
        text_str = self.text if self.text else ""
        bluesky_username_str = (
            self.bluesky_username.bluesky_username if self.bluesky_username else ""
        )
        link_card_title_str = self.link_card_title if self.link_card_title else ""
        link_card_description_str = (
            self.link_card_description if self.link_card_description else ""
        )

        post_object = PostObject(
            id=self.id,
            text=text_str,
            bluesky_username=bluesky_username_str,
            links=self.links(),
            link_card_title=link_card_title_str,
            link_card_description=link_card_description_str,
            is_link_card=self.is_link_card(),
            image_urls_with_alts=self.image_urls_with_alts(),
            reply_to=self.reply_to_int(),
        )
        return post_object

    @admin.display(description="")
    def name_emoji(self) -> str:
        """Generate an emoji derived arbitrarily from the characters in the username.

        There is also an emoji for whether posts are enabled.

        Returns:
            str: Bluesky Username with an emoji for easier identification by eye
        """
        user_config = Config.objects.filter(
            bluesky_username=self.bluesky_username
        ).first()
        if user_config:
            return get_name_emoji(user_config.bluesky_username)
        else:
            return "❓"

    @admin.display(description="")
    def posts_enabled(self) -> str:
        user_config = Config.objects.filter(
            bluesky_username=self.bluesky_username
        ).first()
        if user_config:
            publish_flag = PUBLISH_STATUS_EMOJIS["disabled"]
            if user_config.allow_posts:
                publish_flag = PUBLISH_STATUS_EMOJIS["enabled"]
            return publish_flag
        else:
            return "❓"

    @admin.display(description="Post Details")
    def post_details(self) -> str:
        post_object = self.post_object()

        link_num = len(self.links())
        image_num = len(post_object.image_urls_with_alts)

        detail_items = []

        if image_num:
            detail_items.append(f"{DETAIL_EMOJIS['image']}{image_num}")
        if link_num:
            if self.is_link_card():
                detail_items.append(DETAIL_EMOJIS["link_card"])
            else:
                detail_items.append(f"{DETAIL_EMOJIS['link']}{link_num}")
        if self.reply_to_int():
            detail_items.append(DETAIL_EMOJIS["reply"])

        return ",".join(detail_items)

    def __str__(self):
        return f"{self.id}_{self.bluesky_username}_{self.text[:50]}"
