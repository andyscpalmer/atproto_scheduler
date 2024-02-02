from django.contrib import admin
from django.db import models


class Config(models.Model):
    bluesky_username = models.CharField(max_length=100, primary_key=True, unique=True)
    app_password = models.CharField(max_length=50)

    interval_hours = models.IntegerField(default=12)
    interval_minutes = models.IntegerField(default=0)

    allow_posts = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Bluesky user configuration"
        verbose_name_plural = "Bluesky user configurations"
        ordering = ["bluesky_username"]

    def __str__(self):
        return self.bluesky_username


class Post(models.Model):

    text = models.TextField(max_length=300)
    bluesky_username = models.ForeignKey(Config, on_delete=models.CASCADE, null=True, blank=True)
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

    class Meta:
        ordering = ["-created_at"]

    @admin.display(description="Post snippet")
    def post_snippet(self):
        return self.text[:100]

    def __str__(self):
        return f"{self.id}_{self.text[:50]}"
