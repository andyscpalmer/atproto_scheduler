from datetime import timedelta

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from posts.models import Post, Config


class BaseConfigForm(forms.Form):
    bluesky_username = forms.CharField(max_length=100)
    app_password = forms.CharField(max_length=50)
    interval = forms.DurationField()
    allow_posts = forms.BooleanField()

    def clean_user_data(self):
        data = self.cleaned_data["interval"]

        if data < timedelta(minutes=1):
            raise ValidationError(_("Interval too short"))

        return data


class ConfigModelForm(forms.ModelForm):

    class Meta:
        model = Config
        fields = ["bluesky_username", "app_password", "interval", "allow_posts"]

    def clean_user_data(self):
        data = self.cleaned_data["interval"]

        if data < timedelta(minutes=1):
            raise ValidationError(_("Interval too short"))

        return data


# class BasePost(forms.ModelForm):

#     class Meta:
#         model = Post

#         text = ""

#         fieldsets = [
#             (
#                 None,
#                 {
#                     "classes": ["extrapretty"],
#                     "fields": [
#                         "text",
#                         "bluesky_username",
#                         "is_draft",
#                         "scheduled_post_time",
#                         "reply_to",
#                     ],
#                 },
#             ),
#             (
#                 "Add links",
#                 {
#                     "classes": ["collapse", "extrapretty"],
#                     "fields": [
#                         ("link_1", "link_card_title", "link_card_description"),
#                         "link_2",
#                         "link_3",
#                         "link_4",
#                     ],
#                 },
#             ),
#             (
#                 "Add images",
#                 {
#                     "classes": ["collapse", "extrapretty"],
#                     "fields": [
#                         ("image_1", "alt_1"),
#                         ("image_2", "alt_2"),
#                         ("image_3", "alt_3"),
#                         ("image_4", "alt_4"),
#                     ],
#                 },
#             ),
#             (
#                 "Reset posted info",
#                 {
#                     "classes": ["collapse", "extrapretty"],
#                     "fields": ["posted_at", "cid", "uri"],
#                 },
#             ),
#             (
#                 "Metadata",
#                 {
#                     "classes": ["collapse", "extrapretty"],
#                     "fields": ["error", "created_at", "updated_at"],
#                 },
#             ),
#         ]
