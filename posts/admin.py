from datetime import timedelta

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# from posts.forms import BaseConfigForm, ConfigModelForm
from posts.models import Post, Config
from schedule_client.utils.s3 import ImageClient


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
        "post_details",
        "name_emoji",
        "bluesky_username",
        "posts_enabled",
        "post_status",
        "scheduled_post_time",
    ]
    list_filter = ["bluesky_username", "post_status", "scheduled_post_time"]
    readonly_fields = [
        "image_tag_1",
        "image_tag_2",
        "image_tag_3",
        "image_tag_4",
        "error",
        "created_at",
        "updated_at",
    ]
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
                    "reply_to",
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
                    ("image_tag_1", "image_1", "alt_1"),
                    ("image_tag_2", "image_2", "alt_2"),
                    ("image_tag_3", "image_3", "alt_3"),
                    ("image_tag_4", "image_4", "alt_4"),
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

    def image_tag_1(self, obj):
        if obj.image_1:
            img_cli = ImageClient()
            return mark_safe(img_cli.get_image_tag(obj.image_1.name))
        else:
            return "(no image)"

    def image_tag_2(self, obj):
        if obj.image_2:
            img_cli = ImageClient()
            return mark_safe(img_cli.get_image_tag(obj.image_2.name))
        else:
            return "(no image)"

    def image_tag_3(self, obj):
        if obj.image_3:
            img_cli = ImageClient()
            return mark_safe(img_cli.get_image_tag(obj.image_3.name))
        else:
            return "(no image)"

    def image_tag_4(self, obj):
        if obj.image_4:
            img_cli = ImageClient()
            return mark_safe(img_cli.get_image_tag(obj.image_4.name))
        else:
            return "(no image)"


def validate_interval(interval: timedelta):
    if interval < timedelta(minutes=1):
        raise ValidationError(_("Interval is too short"))


class ConfigModelForm(forms.ModelForm):
    class Meta:
        model = Config
        fields = ["bluesky_username", "app_password", "interval", "allow_posts"]

    interval = forms.DurationField(validators=[validate_interval])

    def clean_user_data(self):
        data = self.cleaned_data["interval"]

        if data < timedelta(minutes=1):
            raise ValidationError(_("Interval too short"))

        return data


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = [
        "name_with_emoji",
        "interval",
        "publishing_status",
    ]
    form = ConfigModelForm
