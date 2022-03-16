from typing import Optional
from beanie import Document, Indexed


class Config(Document):
    """Server Config Model"""

    guild_id: Indexed(int, unique=True)
    auto_embed: Optional[bool] = True
    delete_origin: Optional[bool] = False
    suppress_origin_embed: Optional[bool] = True
    language: Optional[str] = "en"
