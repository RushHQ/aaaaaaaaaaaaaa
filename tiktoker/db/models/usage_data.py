from typing import Optional
from beanie import Document, Indexed
from pydantic.fields import Field
from datetime import datetime


class UsageData(Document):
    """Usage Data Model"""

    guild_id: int
    user_id: Optional[int] = None
    video_id: int
    message_id: Optional[int] = None
    entry_time: datetime = Field(default=datetime.utcnow())
