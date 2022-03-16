from beanie import Document, Indexed

class Shortener(Document):
    """Opted Out Model"""

    video_uri: Indexed(str, unique=True)
    slug: Indexed(str, unique=True)
    shortened_url: Indexed(str)  # full url