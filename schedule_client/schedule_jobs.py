from posts.models import Post
from schedule_client.utils.atproto_client import AtprotoClient
from schedule_client.utils.django_client import PostClient, ConfigClient


def schedule_and_post() -> None:
    """Container function for scheduled operations
    """    
    try:
        config = ConfigClient()
    except:
        raise

    if config.allow_posts and not config.is_placeholder:

        try:
            post_client = PostClient()
            post_client.clear_past_scheduled_times()
            post_client.schedule_unscheduled_posts()
            
            scheduled_posts = post_client.get_scheduled_posts()
        except Exception as e:
            print(e)
            raise

        if scheduled_posts:
            atproto_client = AtprotoClient(config.bluesky_username, config.bluesky_password)
            if atproto_client.is_valid_login:
                for scheduled_post in scheduled_posts:
                    print(f"Posting: {scheduled_post.__str__}")
                    atproto_client.post_to_account(scheduled_post)
    
    elif config.is_placeholder:
        print("Note, your Bluesky username is currently a placeholder in Config.")
        print("Please update with valid credentials.")
    else:
        print("Config toggle 'allow_posts' is set to false. Activate to begin scheduled posting.")