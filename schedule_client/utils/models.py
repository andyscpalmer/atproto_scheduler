from pydantic import BaseModel, Field

class PostObject(BaseModel):
    id: int
    text: str = Field(default="", max_length=300)
    links: list[str] = Field(default=[], max_length=4)
    link_card_title: str = Field(default="")
    link_card_description: str = Field(default="")
    is_link_card: bool = Field(default=False)
    image_urls_with_alts: list[dict] = Field(default=[], max_length=4)