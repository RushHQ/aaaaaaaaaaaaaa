from typing import Optional
from beanie import Document, Indexed


class Shortener(Document):
    """Opted Out Model"""

    video_uri: Indexed(str, unique=True)
    slug: Indexed(str, unique=True)
    shortened_url: Indexed(str)  # full url
    douyin: Optional[bool] = False
