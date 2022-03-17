import aiohttp
import dis_snek as dis
from tiktoker.utils import (
    check_for_link,
    create_short_url,
    get_guild_config,
    insert_usage_data,
)
from tiktoker.utils.translate import load_lang
from tiktoker import BROWSER
import json
import urllib.parse

_ = load_lang("douyin")
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"


class Douyin(dis.Scale):
    def __init__(self, bot: dis.Snake):
        self.bot = bot

    @dis.listen(dis.events.MessageCreate)
    async def on_message_create(self, event: dis.events.MessageCreate):
        if event.message.author.bot:
            return
        link = check_for_link(event.message.content)
        if not link or not link.douyin:
            return

        await event.message.channel.trigger_typing()
        page = await BROWSER.newPage()
        await page.setUserAgent(user_agent)
        await page.goto(link.url)
        element = await page.querySelector("#RENDER_DATA")
        video_data = await page.evaluate("(element) => element.innerText", element)
        await page.close()
        decoded = urllib.parse.unquote(video_data)
        video_data = json.loads(decoded)
        long_video_id = video_data["32"]["aweme"]["detail"]["video"]["playApi"]
        video_id = video_data["32"]["awemeId"]
        long_video_id = (
            long_video_id.split("?")[1].split("&")[0].split("=")[1]
        )  # get id
        short_url = await create_short_url(long_video_id, True)
        more_info_btn = dis.Button(dis.ButtonStyles.URL, "Download", url=short_url)
        delete_msg_btn = dis.Button(
            dis.ButtonStyles.RED,
            emoji="🗑️",
            custom_id=f"delete{event.message.author.id}",
        )
        too_big = False
        config = await get_guild_config(event.message.guild.id)

        async with aiohttp.ClientSession() as session:
            async with session.head(
                short_url, allow_redirects=True, headers={"user-agent": user_agent}
            ) as response:
                video_url = response.headers.get("location")
            async with session.head(video_url, allow_redirects=True) as response:
                video_size = response.headers.get("content-length")

        if int(video_size) > 50000000:  # 50mb | This is Discord's limit for embeds
            too_big = _[config.language].gettext(
                "This video may be too long/big for Discord to embed. Just visit the link above."
            )

        if config.delete_origin:
            message = _[config.language].gettext("%s | From: %s %s") % (
                short_url,
                event.message.author.mention,
                "\n" + too_big if too_big else "",
            )
            sent_msg = await event.message.channel.send(
                message,
                components=[more_info_btn, delete_msg_btn],
                allowed_mentions=dis.AllowedMentions.none(),
            )
            try:
                await event.message.delete()
            except dis.errors.NotFound:
                pass
        elif config.suppress_origin_embed:
            await event.message.suppress_embeds()
            await self.bot.fetch_channel(event.message._channel_id)
            message = short_url + ("\n" + too_big if too_big else "")
            sent_msg = await event.message.reply(
                message, components=[more_info_btn, delete_msg_btn]
            )
        else:
            await self.bot.fetch_channel(event.message._channel_id)
            message = short_url + ("\n" + too_big if too_big else "")
            sent_msg = await event.message.reply(
                message, components=[more_info_btn, delete_msg_btn]
            )

        await insert_usage_data(
            event.message.guild.id, event.message.author.id, video_id, sent_msg.id
        )


def setup(bot: dis.Snake):
    Douyin(bot)
