from typing import Optional
from beanie import Document, Indexed
from pydantic.fields import Field


class OptedOut(Document):
    """Opted Out Model"""

    user_id: Indexed(int, unique=True)
