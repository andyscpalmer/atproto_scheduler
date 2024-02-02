from datetime import timedelta

from django.utils import timezone

from atproto_scheduler.settings import SCHEDULER_INTERVAL
from posts.models import Post, Config
from schedule_client.utils.data_models import PostObject, AccountObject

class PostClient():
    """Handle interactions with post table
    """    
    def __init__(self) -> None:
        self.non_draft_unpublished_posts = Post.objects.filter(is_draft=False).filter(posted_at=None)
        self.scheduled_posts = self.non_draft_unpublished_posts.exclude(scheduled_post_time=None)


    def clear_past_scheduled_times(self) -> None:
        """Remove scheduled times for unposted elements that are scheduled in the past
        """        
        past_scheduled_posts = self.non_draft_unpublished_posts.filter(scheduled_post_time__lt=timezone.now()).all()

        for past_scheduled_post in past_scheduled_posts:
            past_scheduled_post.scheduled_post_time = None
            past_scheduled_post.save()


    def schedule_unscheduled_posts(self, account: AccountObject) -> None:
        """Produce a list of all unscheduled posts and distribute them evenly at pre-configured interval

        Args:
            account (AccountObject): The Bluesky account whose posts are being scheduled
        """        
        # Get all unscheduled posts
        unscheduled_posts = (self.non_draft_unpublished_posts
                                .filter(bluesky_username=account.bluesky_username)
                                .filter(scheduled_post_time=None)
                                .all())
        interval = timedelta(
            hours=account.interval_hours,
            minutes=account.interval_minutes
        )

        if unscheduled_posts:
            # Get time of last scheduled post - Reference time
            last_scheduled_post = self.scheduled_posts.order_by("-scheduled_post_time").first()

            if last_scheduled_post:
                reference_time = last_scheduled_post.scheduled_post_time + interval
            else:
                reference_time = timezone.now() + timedelta(minutes=1)

            # Loop through all unscheduled posts
            for unscheduled_post in unscheduled_posts:
                # Set scheduled time to reference time plus interval
                print(f"Setting {unscheduled_post.__str__} to time {reference_time}")
                unscheduled_post.scheduled_post_time = reference_time
                unscheduled_post.save()

                # Update reference time to scheduled time used
                reference_time += interval


    def get_scheduled_posts(self, account: AccountObject) -> list[PostObject]:
        """Collect all unscheduled posts within the SCHEDULER_INTERVAL before and after timezone.now().

        Args:
            account (AccountObject): The Bluesky account whose posts are being retrieved

        Returns:
            list[PostObject]: List of all posts within scheduler interval
        """

        account_filtered_posts = self.scheduled_posts.filter(bluesky_username=account.bluesky_username)

        schedule_window_begin = timezone.now() - SCHEDULER_INTERVAL
        schedule_window_end = timezone.now() + SCHEDULER_INTERVAL
        
        posts_within_window = account_filtered_posts.exclude(scheduled_post_time__lt=schedule_window_begin).exclude(scheduled_post_time__gt=schedule_window_end).all()

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
                bluesky_username=account.bluesky_username,
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
        self.check_placeholder_status()
        self.accounts = []

        if not self.is_placeholder:
            self.populate_bluesky_accounts()

    
    def populate_bluesky_accounts(self) -> None:
        """Populate Bluesky user data into self.accounts
        """        
        raw_accounts = Config.objects.all()
        for raw_account in raw_accounts:
            account = AccountObject(
                bluesky_username=raw_account.bluesky_username,
                bluesky_password=raw_account.app_password,
                interval_hours=raw_account.interval_hours,
                interval_minutes=raw_account.interval_minutes,
                allow_posts=raw_account.allow_posts
            )
            self.accounts.append(account)


    def check_placeholder_status(self) -> None:
        """Check for presence of configurations. Adds placeholder if none exists.
        """        
        is_one_config_entry = len(Config.objects.all())
        is_first_placeholder = Config.objects.first().bluesky_username == "placeholder"

        if is_one_config_entry and is_first_placeholder:
            self.is_placeholder = True
