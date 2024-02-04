from datetime import timedelta

from pydantic import BaseModel, Field


class PostObject(BaseModel):
    id: int
    text: str = Field(default="", max_length=300)
    bluesky_username: str = Field(default="")
    links: list[str] = Field(default=[], max_length=4)
    link_card_title: str = Field(default="")
    link_card_description: str = Field(default="")
    is_link_card: bool = Field(default=False)
    image_urls_with_alts: list[dict] = Field(default=[], max_length=4)


class AccountObject(BaseModel):
    bluesky_username: str = Field(default="")
    bluesky_password: str = Field(default="")
    interval: timedelta = Field(default=timedelta(hours=12))
    allow_posts: bool = Field(default=False)
