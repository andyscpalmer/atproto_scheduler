from django.db import models

class Post(models.Model):

    text = models.TextField(max_length=300)
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
    created_at = models.DateTimeField(auto_now=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    cid = models.CharField(max_length=300, null=True, blank=True)
    uri = models.CharField(max_length=300, null=True, blank=True)
    scheduled_post_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.id}_{self.text[:50]}"


class Config(models.Model):
    bluesky_username = models.CharField(max_length=100)
    app_password = models.CharField(max_length=50)

    interval_hours = models.IntegerField(default=12)
    interval_minutes = models.IntegerField(default=0)

    allow_posts = models.BooleanField(default=False)

    def __str__(self):
        return self.bluesky_username
