from base64 import urlsafe_b64encode
from typing import Optional, List
import aiohttp
from tiktoker.db.models import Config, OptedOut, UsageData, Shortener
from tiktoker.models import LinkData, VideoIdType, TikTokData
import re
from pymongo.errors import DuplicateKeyError
from os import urandom, walk


async def get_tiktok(video_id: int) -> Optional["TikTokData"]:
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(5)) as session:
        async with session.get(
            f"https://api2.musical.ly/aweme/v1/aweme/detail/?aweme_id={video_id}",
            allow_redirects=False,
        ) as response:
            data = await response.json()
            if data.get("aweme_detail") and data.get("status_code") == 0:
                return TikTokData.from_dict(data["aweme_detail"])
            raise ValueError("Unable to get TikTok data")


async def get_music_data(music_id: int = None) -> Optional[dict]:
    """
    Gets the music data.

    args:
        music_id: The music id.

    returns:
        The music data.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://tiktok.com/api/music/detail/?language=en&musicId={music_id}",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0"
            },
        ) as response:
            if response.status == 200:
                if data := await response.json():
                    if data.get("statusCode") == 10218:
                        return None
                    return data
                return data
            else:
                return None


def get_scales(path: str) -> list:
    """Get scales"""
    files = [thing for thing in walk(path)][0][2]
    scales = [x.replace(".py", "").replace(" ", "_") for x in files]
    return ["tiktoker.scales.{}".format(x) for x in scales]


async def get_guild_config(guild_id: int) -> "Config":
    """
    Gets the guild config.

    args:
        guild_id: The guild id.

    returns:
        The guild config.
    """
    if config := await Config.find_one({"guild_id": guild_id}):
        return config
    else:
        new_config = Config(guild_id=guild_id)
        await new_config.save()
        return new_config


async def edit_guild_config(guild_id: int, **kwargs) -> "Config":
    config = await get_guild_config(guild_id)
    for key, value in kwargs.items():
        await config.update({key: value})
    return await get_guild_config(guild_id)


async def insert_usage_data(
    guild_id: int, user_id: int, video_id: int, message_id: int
) -> None:
    """
    Inserts usage data.

    args:
        guild_id: The guild id.
        user_id: The user id.
        video_id: The video id.
        message_id: The message id with the video.
    """

    if await get_opted_out(user_id):  # weirdos
        user_id = None
        message_id = None

    await UsageData(
        guild_id=guild_id, user_id=user_id, video_id=video_id, message_id=message_id
    ).save()


async def get_guild_usage_data(guild_id: int) -> List["UsageData"]:
    """
    Gets the guild usage data.

    args:
        guild_id: The guild id.

    returns:
        The guild usage data.
    """
    return await UsageData.find({"guild_id": guild_id}).to_list()


async def get_user_usage_data(user_id: int) -> List["UsageData"]:
    """
    Gets the user usage data.

    args:
        user_id: The user id.

    returns:
        The user usage data.
    """
    return await UsageData.find({"user_id": user_id}).to_list()


async def get_all_usage_data() -> List["UsageData"]:
    """
    Gets all usage data.

    returns:
        The all usage data.
    """
    return await UsageData.find_all().to_list()


async def add_opted_out(user_id: int) -> None:
    await OptedOut(user_id=user_id).save()


async def remove_opted_out(user_id: int) -> None:
    await OptedOut.find_one({"user_id": user_id}).delete()


async def remove_usage_data(guild_id: int, user_id: int) -> None:
    usage_data = UsageData.find({"guild_id": guild_id, "user_id": user_id})
    await usage_data.update_many().set({"message_id": None, "user_id": None})


async def get_opted_out(user_id: int) -> bool:
    if opted_out := await OptedOut.find_one({"user_id": user_id}):
        return True
    else:
        return False


def check_for_link(content: str) -> Optional["LinkData"]:
    """
    Checks if the content has a TikTok video.

    args:
        content: The content to check.

    returns:
        LinkData
    """
    try:
        fyp_match = re.search(
            r"(?P<http>http:|https:\/\/)?(www)?\.tiktok.com\/(.*)item_id=(?P<item_id>\d{5,30})",
            content,
        )
        long_match = re.search(
            r"(?P<http>http:|https:\/\/)?(www\.)?tiktok\.com\/(@.{1,24})\/video\/(?P<id>\d{15,30})",
            content,
        )
        short_match = re.search(
            r"(?P<http>http:|https:\/\/)?((?!ww)\w{2})\.tiktok.com\/(?P<short_id>\w{5,15})",
            content,
        )
        medium_match = re.search(
            r"(?P<http>http:|https:\/\/)?m\.tiktok\.com\/v\/(?P<id>\d{15,30})", content
        )
    except TypeError as e:
        print(f"{content} is not a string")
        print(type(content))
    if long_match:
        if not long_match.group("http"):
            return LinkData.from_list(
                [
                    VideoIdType.LONG,
                    long_match.group("id"),
                    f"https://{long_match.group(0)}",
                ]
            )
        return LinkData.from_list(
            [VideoIdType.LONG, long_match.group("id"), long_match.group(0)]
        )
    if short_match:
        if not short_match.group("http"):
            return LinkData.from_list(
                [
                    VideoIdType.SHORT,
                    short_match.group("short_id"),
                    f"https://{short_match.group(0)}",
                ]
            )
        return LinkData.from_list(
            [VideoIdType.SHORT, short_match.group("short_id"), short_match.group(0)]
        )
    if medium_match:
        if not medium_match.group("http"):
            return LinkData.from_list(
                [
                    VideoIdType.MEDIUM,
                    medium_match.group("id"),
                    f"https://{medium_match.group(0)}",
                ]
            )
        return LinkData.from_list(
            [VideoIdType.MEDIUM, medium_match.group("id"), medium_match.group(0)]
        )
    if fyp_match:
        if not fyp_match.group("http"):
            return LinkData.from_list(
                [
                    VideoIdType.FYP,
                    fyp_match.group("item_id"),
                    f"https://{fyp_match.group(0)}",
                ]
            )
        return LinkData.from_list(
            [VideoIdType.FYP, fyp_match.group("item_id"), fyp_match.group(0)]
        )
    return None


async def create_short_url(video_uri: str) -> str:
    """
    Shortens a url if not in cache.

    args:
        video_uri: The uri of the video.

    returns:
        The shortened url.
    """

    if existing_entry := await Shortener.find_one({"video_uri": video_uri}):

        return existing_entry.shortened_url

    slug = urlsafe_b64encode(urandom(6)).decode()
    while await Shortener.find_one({"slug": slug}) != None:
        print("Note: slug collision, regenerating")
        slug = urlsafe_b64encode(urandom(6)).decode()

    shortener = Shortener(
        video_uri=video_uri,
        slug=slug,
        shortened_url=f"https://m.tiktoker.win/{slug}",
    )
    try:
        await shortener.save()
    except DuplicateKeyError:
        # NOTE: This can be triggered when someone spams the link
        #       so we just ignore it and return the existing url.
        ...
    return shortener.shortened_url


async def get_video_id(url: str) -> int:
    """
    Gets the video id from short url.

    args:
        url: The url to get the id from.

    returns:
        The video id.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url, allow_redirects=False) as response:
            if location := response.headers.get("Location"):
                if link := check_for_link(location):
                    return link.id
