from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from posts.utils.constants import PUBLISH_STATUS_EMOJIS
from posts.models import Post, Config
from schedule_client.utils.django_client import PostClient, ConfigClient

class PostTestCase(TestCase):
    def setUp(self):
        Config.objects.create(
            bluesky_username="testname_1",
            app_password="testpass123",
            interval=timedelta(minutes=1),
            allow_posts=True,
        )
        Config.objects.create(
            bluesky_username="testname_2",
            app_password="testpass321",
            interval=timedelta(hours=2),
            allow_posts=False
        )

        test_user_1 = Config.objects.get(bluesky_username="testname_1")
        test_user_2 = Config.objects.get(bluesky_username="testname_2")

        Post.objects.create(
            id=1,
            text="foo",
            bluesky_username=test_user_1,
            is_draft=False,
            scheduled_post_time=timezone.now()
        )
        Post.objects.create(
            id=2,
            text="bar",
            bluesky_username=test_user_1,
            link_1="https://www.example.com/",
            link_card_title="Example website",
            link_card_description="Example description",
            reply_to=Post.objects.get(id=1),
            is_draft=True,
        )
        Post.objects.create(
            id=3,
            text="bat",
            bluesky_username=test_user_2,
            image_1="test/image.png",
            alt_1="test alt text",
            is_draft=False
        )
        Post.objects.create(
            id=4,
            text="baz",
            bluesky_username=test_user_1,
            is_draft=False,
            scheduled_post_time=timezone.now() - timedelta(minutes=5),
            posted_at=timezone.now(),
            cid="abc",
            uri="def",
        )
        Post.objects.create(
            id=5,
            text="blugh",
            bluesky_username=test_user_1,
            reply_to=Post.objects.get(id=4),
            is_draft=False
        )

    def test_create_config_object(self):
        test_user_1 = Config.objects.get(bluesky_username="testname_1")
        test_user_2 = Config.objects.get(bluesky_username="testname_2")

        self.assertEqual(test_user_1.bluesky_username, "testname_1")
        self.assertEqual(test_user_1.app_password, "testpass123")
        self.assertEqual(test_user_1.interval, timedelta(minutes=1))
        self.assertEqual(test_user_1.allow_posts, True)

        self.assertEqual(test_user_2.bluesky_username, "testname_2")
        self.assertEqual(test_user_2.app_password, "testpass321")
        self.assertEqual(test_user_2.interval, timedelta(hours=2))
        self.assertEqual(test_user_2.allow_posts, False)

    
    def test_create_post_object(self):
        post_1 = Post.objects.get(id=1)
        post_2 = Post.objects.get(id=2)
        post_3 = Post.objects.get(id=3)

        test_user_1 = Config.objects.get(bluesky_username="testname_1")
        test_user_2 = Config.objects.get(bluesky_username="testname_2")

        self.assertEqual(post_1.text, "foo")
        self.assertEqual(post_1.bluesky_username, test_user_1)
        self.assertEqual(post_1.cid, None)
        self.assertEqual(post_1.is_draft, False)

        self.assertEqual(post_2.text, "bar")
        self.assertEqual(post_2.bluesky_username, test_user_1)
        self.assertEqual(post_2.link_1, "https://www.example.com/")
        self.assertEqual(post_2.link_card_title, "Example website")
        self.assertEqual(post_2.link_card_description, "Example description")
        self.assertEqual(post_2.reply_to, post_1)
        self.assertEqual(post_2.is_draft, True)
        self.assertEqual(post_2.post_status, "📝 Draft")

        self.assertEqual(post_3.text, "bat")
        self.assertEqual(post_3.bluesky_username, test_user_2)
        self.assertEqual(post_3.image_1, "test/image.png")
        self.assertEqual(post_3.alt_1, "test alt text")
        self.assertEqual(post_3.is_draft, False)
        self.assertEqual(post_3.post_status, "⏳ Scheduled")

    # def test_django_client(self):
    #     post_1 = Post.objects.get(id=1)
    #     post_2 = Post.objects.get(id=2)
    #     post_3 = Post.objects.get(id=3)
    #     post_4 = Post.objects.get(id=4)
    #     post_5 = Post.objects.get(id=5)

    #     test_user_1 = Config.objects.get(bluesky_username="testname_1")
    #     test_user_2 = Config.objects.get(bluesky_username="testname_2")

    #     post_client = PostClient()
    #     scheduled_posts = post_client.get_scheduled_posts(test_user_1)
    #     self.assertEqual(scheduled_posts[0], post_1)
