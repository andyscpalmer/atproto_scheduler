from datetime import timedelta

from django.utils import timezone

from atproto_scheduler.settings import SCHEDULER_INTERVAL
from posts.models import Post, Config
from schedule_client.utils.models import PostObject

class PostClient():
    """Handle interactions with post table
    """    
    def __init__(self) -> None:
        self.config = Config.objects.first()
        self.interval = timedelta(
            hours=self.config.interval_hours,
            minutes=self.config.interval_minutes
        )
        self.non_draft_unpublished_posts = Post.objects.filter(is_draft=False).filter(posted_at=None)
        self.scheduled_posts = self.non_draft_unpublished_posts.exclude(scheduled_post_time=None)


    def clear_past_scheduled_times(self) -> None:
        """Remove scheduled times for unposted elements that are scheduled in the past
        """        
        past_scheduled_posts = self.non_draft_unpublished_posts.filter(scheduled_post_time__lt=timezone.now()).all()

        for past_scheduled_post in past_scheduled_posts:
            past_scheduled_post.scheduled_post_time = None
            past_scheduled_post.save()


    def schedule_unscheduled_posts(self) -> None:
        """Produce a list of all unscheduled posts and distribute them evenly at pre-configured interval
        """        
        # Get all unscheduled posts
        unscheduled_posts = self.non_draft_unpublished_posts.filter(scheduled_post_time=None).all()

        if unscheduled_posts:

            # Get time of last scheduled post - Reference time
            last_scheduled_post = self.scheduled_posts.order_by("-scheduled_post_time").first()

            if last_scheduled_post:
                reference_time = last_scheduled_post.scheduled_post_time + self.interval
            else:
                reference_time = timezone.now() + timedelta(minutes=1)

            # Loop through all unscheduled posts
            for unscheduled_post in unscheduled_posts:
                # Set scheduled time to reference time plus interval
                print(f"Setting {unscheduled_post.__str__} to time {reference_time}")
                unscheduled_post.scheduled_post_time = reference_time
                unscheduled_post.save()

                # Update reference time to scheduled time used
                reference_time += self.interval


    def get_scheduled_posts(self) -> list[PostObject]:
        """Collect all unscheduled posts within the SCHEDULER_INTERVAL before and after timezone.now().

        Returns:
            list[PostObject]: List of all posts within scheduler interval
        """        
        schedule_window_begin = timezone.now() - SCHEDULER_INTERVAL
        schedule_window_end = timezone.now() + SCHEDULER_INTERVAL
        
        posts_within_window = self.scheduled_posts.exclude(scheduled_post_time__lt=schedule_window_begin).exclude(scheduled_post_time__gt=schedule_window_end).all()

        post_objects = []
        for post in posts_within_window:
            links_raw = [post.link_1, post.link_2, post.link_3, post.link_4]
            images_raw = [post.image_1, post.image_2, post.image_3, post.image_4]
            alt_texts_raw = [post.alt_1, post.alt_2, post.alt_3, post.alt_4]

            links = [link for link in links_raw if link]
            images = [image for image in images_raw if image]

            image_urls_with_alts = [
                {"image": images[i], "alt_text": alt_texts_raw[i]}
                for i in range(len(images))
            ]

            link_card_title = post.link_card_title if post.link_card_title else ""
            link_card_description = post.link_card_description if post.link_card_description else ""

            is_link_card = len(links) == 1 and link_card_title != "" and link_card_description != ""

            post_object = PostObject(
                id=post.id,
                text=post.text,
                links=links,
                link_card_title=link_card_title,
                link_card_description=link_card_description,
                is_link_card=is_link_card,
                image_urls_with_alts=image_urls_with_alts,
            )

            print(f"Posting scheduled post")
            print(f"Post ID: {post_object.text}")
            print(f"Post text: {post_object.text}")
            print(f"Post links: {post_object.links}")
            print(f"Post image data: {post_object.image_urls_with_alts}")
            post_objects.append(post_object)
        
        return post_objects
    

    def set_post_as_draft(self, post_id: int) -> None:
        """Set a post as a draft. Used in the event of an error posting to Bluesky

        Args:
            post_id (int): Unique identifier of post
        """        
        try:
            post_to_draft = Post.objects.filter(id=post_id).first()
            post_to_draft.is_draft = True
            post_to_draft.save()
        except:
            raise


    def set_as_posted(self, post_id: int, cid: str, uri: str) -> None:
        """Set a post as published and record relevant data

        Args:
            post_id (int): Unique identifier of post
            cid (str): CID response value from Bluesky
            uri (str): URI response value from Bluesky
        """        
        try:
            posted_object = Post.objects.filter(id=post_id).first()
            posted_object.posted_at = timezone.now()
            posted_object.cid = cid
            posted_object.uri = uri
            posted_object.save()
        except:
            raise


class ConfigClient():
    """Handle interactions with configuration table
    """    

    def __init__(self) -> None:
        self.is_placeholder = False
        self.check_config_and_add_default()
        self.bluesky_username = None
        self.bluesky_password = None
        self.interval_hours = None
        self.interval_minutes = None
        self.allow_posts = None

        if not self.is_placeholder:
            raw_config = Config.objects.first()
            self.bluesky_username = raw_config.bluesky_username
            self.bluesky_password = raw_config.app_password
            self.interval_hours = raw_config.interval_hours
            self.interval_minutes = raw_config.interval_minutes
            self.allow_posts = raw_config.allow_posts

    def check_config_and_add_default(self) -> None:
        """Check for presence of configurations. Adds placeholder if none exists.
        """        
        
        if len(list(Config.objects.all())) < 1:
            print("No configuration detected. Adding placeholder configuration.")
            default_config = Config(
                bluesky_username="placeholder",
                app_password="placeholder",
                interval_hours=12,
                interval_minutes=0,
                allow_posts=False
            )
            default_config.save()
            self.is_placeholder = True
        
        elif Config.objects.first().bluesky_username == "placeholder":
            self.is_placeholder = True
