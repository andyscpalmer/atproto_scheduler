import re
import typing as t

from atproto import Client, models

from schedule_client.utils.django_client import PostClient
from schedule_client.utils.data_models import PostObject, AccountObject
from schedule_client.utils.s3 import ImageClient


class AtprotoClient:
    """Client for interacting with the at protocol"""

    def __init__(self, bluesky_username: str, bluesky_password: str):
        self.bluesky_username = bluesky_username
        self.bluesky_password = bluesky_password

        try:
            self.client = Client()
            self.client.login(self.bluesky_username, self.bluesky_password)
            self.is_valid_login = True
            print("Successfully logged into Bluesky account.")
        except:
            print("Error logging into Bluesky account.")
            self.is_valid_login = False

    def post_to_account(self, post: PostObject) -> bool:
        """Posts to Bluesky

        Args:
            post (PostObject): Post object with all relevant values

        Returns:
            bool: Value indicating success of posting operation
        """
        print(f"Posting to {self.bluesky_username}")

        embed = None
        facets = None
        reply = None
        text = post.text
        post_client = PostClient()

        if post.reply_to:
            print("Post is a reply")
            reply_cid, reply_uri = post_client.get_reply_details(post.id)

            if reply_cid and reply_uri:
                parent_ref = models.ComAtprotoRepoStrongRef.Main(
                    cid=reply_cid,
                    uri=reply_uri,
                )
                reply = models.AppBskyFeedPost.ReplyRef(
                    parent=parent_ref,
                    root=parent_ref
                )
                print(f"Reply object: {reply}")
            else:
                return False

        # Get hyperlinks
        if post.links and not post.is_link_card:
            text += "\n"
            for link in post.links:
                text += f"{link}\n"

            url_positions = self._extract_url_byte_positions(text, aggressive=True)
            facets = []

            for link in url_positions:
                uri = link[0] if link[0].startswith("http") else f"https://{link[0]}"
                facets.append(
                    models.AppBskyRichtextFacet.Main(
                        features=[models.AppBskyRichtextFacet.Link(uri=uri)],
                        index=models.AppBskyRichtextFacet.ByteSlice(
                            byte_start=link[1], byte_end=link[2]
                        ),
                    )
                )

        # Check for images. If present, post with images.
        if post.image_urls_with_alts:
            images = []
            image_client = ImageClient()

            for image_with_alt in post.image_urls_with_alts:
                image_object = image_client.get_image_object(image_with_alt["image"])

                if not image_object:
                    print(f"Error with image path: {image_with_alt['image']}")
                    print(f"Setting {post.text} as draft.")
                    post_client.set_post_as_draft(post.id)
                    return False

                upload = self.client.com.atproto.repo.upload_blob(image_object)
                images.append(
                    models.AppBskyEmbedImages.Image(
                        alt=image_with_alt["alt_text"], image=upload.blob
                    )
                )

            embed = models.AppBskyEmbedImages.Main(images=images)

            image_client.close()

        # If no images, check for single link item with a title and description. If present, post with link card.
        elif post.is_link_card:
            embed = models.AppBskyEmbedExternal.Main(
                external=models.AppBskyEmbedExternal.External(
                    title=post.link_card_title,
                    description=post.link_card_description,
                    uri=post.links[0],
                )
            )

        try:
            post_response = self.client.com.atproto.repo.create_record(
                models.ComAtprotoRepoCreateRecord.Data(
                    repo=self.client.me.did,
                    collection=models.ids.AppBskyFeedPost,
                    record=models.AppBskyFeedPost.Main(
                        created_at=self.client.get_current_time_iso(),
                        text=text,
                        facets=facets,
                        embed=embed,
                        reply=reply,
                    ),
                )
            )
            post_client.set_as_posted(post.id, post_response.cid, post_response.uri)
            print("Successfully posted to Bluesky.")
            post_client.record_error(post.id, "")
        except Exception as err:
            print(f"Error with post: {post.text[:50]}")
            print(f"Setting {post.text[:50]} as draft.")
            post_client.set_post_as_draft(post.id)
            post_client.record_error(post.id, err)
            print(err)
            return False

        return True

    def _extract_url_byte_positions(
        self, text: str, *, aggressive: bool, encoding: str = "UTF-8"
    ) -> t.List[t.Tuple[str, int, int]]:
        """If aggressive is False, only links beginning http or https will be detected"""
        encoded_text = text.encode(encoding)

        if aggressive:
            pattern = rb"(?:[\w+]+\:\/\/)?(?:[\w\d-]+\.)*[\w-]+[\.\:]\w+\/?(?:[\/\?\=\&\#\.]?[\w-]+)+\/?"
        else:
            pattern = rb"https?\:\/\/(?:[\w\d-]+\.)*[\w-]+[\.\:]\w+\/?(?:[\/\?\=\&\#\.]?[\w-]+)+\/?"

        matches = re.finditer(pattern, encoded_text)
        url_byte_positions = []
        for match in matches:
            url_bytes = match.group(0)
            url = url_bytes.decode(encoding)
            url_byte_positions.append((url, match.start(), match.end()))

        return url_byte_positions
