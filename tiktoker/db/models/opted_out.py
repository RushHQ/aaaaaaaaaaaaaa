from beanie import Document, Indexed


class OptedOut(Document):
    """Opted Out Model"""

    user_id: Indexed(int, unique=True)
