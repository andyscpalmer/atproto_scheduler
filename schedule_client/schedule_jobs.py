from datetime import datetime
from threading import get_ident

from schedule_client.utils.atproto_client import AtprotoClient
from schedule_client.utils.data_models import AccountObject
from schedule_client.utils.django_client import PostClient, ConfigClient


def schedule_and_post() -> None:
    """Container function for scheduled operations"""
    try:
        config = ConfigClient()
    except:
        raise

    if not config.is_placeholder:
        post_client = PostClient()
        post_client.clear_past_scheduled_times()

        for account in config.accounts:
            handle_account_posts(post_client, account)


def handle_account_posts(post_client: PostClient, account: AccountObject) -> None:
    """Handle post actions for individual accounts

    Args:
        post_client (PostClient): Object for interacting with the Posts table
        account (AccountObject): Account details
    """
    if account.allow_posts:
        try:
            post_client.schedule_unscheduled_posts(account)
            scheduled_posts = post_client.get_scheduled_posts(account)
        except Exception as e:
            print(e)
            raise

        if scheduled_posts:
            try:
                atproto_client = AtprotoClient(
                    account.bluesky_username, account.bluesky_password
                )
                if atproto_client.is_valid_login:
                    for scheduled_post in scheduled_posts:
                        print(f"{get_ident()}: Posting: {scheduled_post.__str__}")
                        atproto_client.post_to_account(scheduled_post)
            finally:
                del atproto_client
