from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from posts.utils.constants import PUBLISH_STATUS_EMOJIS
from posts.models import Post, Config
from posts.utils.constants import PUBLISH_STATUS_EMOJIS, DETAIL_EMOJIS
from schedule_client.utils.django_client import PostClient, ConfigClient
from schedule_client.utils.data_models import PostObject


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
            allow_posts=False,
        )

        test_user_1 = Config.objects.get(bluesky_username="testname_1")
        test_user_2 = Config.objects.get(bluesky_username="testname_2")

        Post.objects.create(
            id=1,
            text="foo",
            bluesky_username=test_user_1,
            is_draft=False,
            scheduled_post_time=timezone.now(),
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
            is_draft=False,
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
            is_draft=False,
        )
        Post.objects.create(
            id=6,
            text="foobar",
            bluesky_username=test_user_1,
            link_1="https://www.example.com/",
            is_draft=False,
        )
        Post.objects.create(
            id=7,
            text="barfoo",
            bluesky_username=test_user_1,
            link_1="https://www.example1.com/",
            link_2="https://www.example2.com/",
            link_3="https://www.example3.com/",
            link_4="https://www.example4.com/",
            is_draft=False,
        )
        Post.objects.create(
            id=8,
            text="barbat",
            bluesky_username=test_user_1,
            image_1="foo/bar1.jpg",
            image_2="foo/bar2.jpg",
            image_3="foo/bar3.png",
            image_4="foo/bar4.jpeg",
            alt_1="foo bar 1",
            alt_2="foo bar 2",
            alt_3="foo bar 3",
            alt_4="foo bar 4",
            is_draft=False,
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

    def test_is_link_card(self):
        post_1 = Post.objects.get(id=1)
        post_2 = Post.objects.get(id=2)
        post_6 = Post.objects.get(id=6)
        post_7 = Post.objects.get(id=7)

        self.assertEqual(post_1.is_link_card(), False)
        self.assertEqual(post_2.is_link_card(), True)
        self.assertEqual(post_6.is_link_card(), False)
        self.assertEqual(post_7.is_link_card(), False)

    def test_links(self):
        post_1 = Post.objects.get(id=1)
        post_2 = Post.objects.get(id=2)
        post_6 = Post.objects.get(id=6)
        post_7 = Post.objects.get(id=7)

        self.assertEqual(post_1.links(), [])
        self.assertEqual(post_2.links(), ["https://www.example.com/"])
        self.assertEqual(post_6.links(), ["https://www.example.com/"])
        self.assertEqual(
            post_7.links(),
            [
                "https://www.example1.com/",
                "https://www.example2.com/",
                "https://www.example3.com/",
                "https://www.example4.com/",
            ],
        )

    def test_image_urls_with_alts(self):
        post_1 = Post.objects.get(id=1)
        post_3 = Post.objects.get(id=3)
        post_8 = Post.objects.get(id=8)

        expected_image_urls_with_alts_1 = []
        self.assertEqual(post_1.image_urls_with_alts(), expected_image_urls_with_alts_1)

        expected_image_urls_with_alts_3 = [
            {"image": "test/image.png", "alt_text": "test alt text"},
        ]
        self.assertEqual(post_3.image_urls_with_alts(), expected_image_urls_with_alts_3)

        expected_image_urls_with_alts_8 = [
            {"image": "foo/bar1.jpg", "alt_text": "foo bar 1"},
            {"image": "foo/bar2.jpg", "alt_text": "foo bar 2"},
            {"image": "foo/bar3.png", "alt_text": "foo bar 3"},
            {"image": "foo/bar4.jpeg", "alt_text": "foo bar 4"},
        ]
        self.assertEqual(post_8.image_urls_with_alts(), expected_image_urls_with_alts_8)

    def test_post_objects(self):
        post_1 = Post.objects.get(id=1)
        expected_post_object_1 = PostObject(
            id=1,
            text="foo",
            bluesky_username="testname_1",
            links=[],
            link_card_title="",
            link_card_description="",
            is_link_card=False,
            image_urls_with_alts=[],
            reply_to=0,
        )
        self.assertEqual(post_1.post_object(), expected_post_object_1)

    def test_post_details(self):

        img_emoji = DETAIL_EMOJIS["image"]
        card_emoji = DETAIL_EMOJIS["link_card"]
        link_emoji = DETAIL_EMOJIS["link"]
        reply_emoji = DETAIL_EMOJIS["reply"]

        post_1 = Post.objects.get(id=1)
        post_details_1 = ""
        self.assertEqual(post_1.post_details(), post_details_1)

        post_2 = Post.objects.get(id=2)
        post_details_2 = f"{card_emoji},{reply_emoji}"
        self.assertEqual(post_2.post_details(), post_details_2)

        post_3 = Post.objects.get(id=3)
        post_details_3 = f"{img_emoji}1"
        self.assertEqual(post_3.post_details(), post_details_3)

        post_7 = Post.objects.get(id=7)
        post_details_7 = f"{link_emoji}4"
        self.assertEqual(post_7.post_details(), post_details_7)

        post_8 = Post.objects.get(id=8)
        post_details_8 = f"{img_emoji}4"
        self.assertEqual(post_8.post_details(), post_details_8)

    def test_django_client(self):
        post_1 = Post.objects.get(id=1)
        test_user_1 = Config.objects.get(bluesky_username="testname_1")
        post_client = PostClient()
        scheduled_posts = post_client.get_scheduled_posts(test_user_1)
        self.assertEqual(scheduled_posts, [post_1.post_object()])
