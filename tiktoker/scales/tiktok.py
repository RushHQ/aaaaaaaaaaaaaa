import dis_snek as dis
from tiktoker.models import TikTokData, VideoIdType
from tiktoker.utils import (
    check_for_link,
    create_short_url,
    get_guild_config,
    get_music_data,
    get_tiktok,
    get_video_id,
    insert_usage_data,
)
from tiktoker.utils.translate import load_lang

_ = load_lang("tiktok")


class TikTok(dis.Scale):
    def __init__(self, bot: dis.Snake):
        self.bot = bot

    @dis.context_menu("Convert 📸", dis.CommandTypes.MESSAGE)
    async def menu_convert_video(self, ctx: dis.InteractionContext):
        await ctx.defer()
        config = await get_guild_config(ctx.guild.id)
        link = check_for_link(ctx.target.content)
        if not link or link.douyin:
            await ctx.send(
                _[config.language].gettext("There is no TikTok link in that message."),
                ephemeral=True,
            )
            return

        if link.type == VideoIdType.SHORT:
            video_id = await get_video_id(link.url)
        else:
            video_id = link.id

        try:
            tiktok = await get_tiktok(video_id)
        except Exception as e:
            await ctx.send(f"Error: {e}", ephemeral=True)
            return

        short_url = await create_short_url(tiktok.video.video_uri)

        more_info_btn = dis.Button(
            dis.ButtonStyles.GRAY,
            "Info",
            "🌐",
            custom_id=f"v_id{video_id}",
        )
        delete_msg_btn = dis.Button(
            dis.ButtonStyles.RED,
            emoji="🗑️",
            custom_id=f"delete{ctx.author.id}",
        )
        if config.suppress_origin_embed:
            await ctx.target.suppress_embeds()

        too_big = False
        if tiktok.video.size > 50000000:
            too_big = _[config.language].gettext(
                "This video may be too long/big for Discord to embed. Just visit the link above."
            )
        message = _[config.language].gettext("%s | [Origin](%s) %s") % (
            short_url,
            ctx.target.jump_url,
            "\n" + too_big if too_big else "",
        )
        sent_msg = await ctx.send(message, components=[more_info_btn, delete_msg_btn])
        await insert_usage_data(ctx.guild.id, ctx.author.id, video_id, sent_msg.id)

    @dis.slash_command("tiktok", "Convert a TikTok link into a video.")
    @dis.slash_option(
        "link", "The TikTok link to convert.", dis.OptionTypes.STRING, True
    )
    async def slash_tiktok(self, ctx: dis.InteractionContext, link: str):
        config = await get_guild_config(ctx.guild.id)
        link = check_for_link(link)
        if not link or link.douyin:
            await ctx.send(
                _[config.language].gettext(
                    "That doesn't seem to be a valid TikTok link."
                ),
                ephemeral=True,
            )
            return

        if link.type == VideoIdType.SHORT:
            video_id = await get_video_id(link.url)
        else:
            video_id = link.id

        try:
            tiktok = await get_tiktok(video_id)
        except Exception as e:
            await ctx.send(f"Error: {e}", ephemeral=True)
            return

        short_url = await create_short_url(tiktok.video.video_uri)
        more_info_btn = dis.Button(
            dis.ButtonStyles.GRAY,
            "Info",
            "🌐",
            custom_id=f"v_id{video_id}",
        )
        delete_msg_btn = dis.Button(
            dis.ButtonStyles.RED,
            emoji="🗑️",
            custom_id=f"delete{ctx.author.id}",
        )
        too_big = False
        if tiktok.video.size > 50000000:
            too_big = _[config.language].gettext(
                "This video may be too long/big for Discord to embed. Just visit the link above."
            )
        message = short_url + ("\n" + too_big if too_big else "")
        sent_msg = await ctx.send(message, components=[more_info_btn, delete_msg_btn])
        await insert_usage_data(ctx.guild.id, ctx.author.id, video_id, sent_msg.id)

    @dis.listen(dis.events.MessageCreate)
    async def on_message_create(self, event: dis.events.MessageCreate):
        if event.message.author.id == self.bot.user.id:
            return
        content = event.message.content
        link = check_for_link(content)
        if not link or link.douyin:
            return

        config = await get_guild_config(event.message.guild.id)

        if not config.auto_embed:
            return

        await event.message.channel.trigger_typing()

        if link.type == VideoIdType.SHORT:
            video_id = await get_video_id(link.url)
        else:
            video_id = link.id

        try:
            tiktok = await get_tiktok(video_id)
        except Exception as e:
            print(f"Error: {e}")
            return

        short_url = await create_short_url(tiktok.video.video_uri)

        more_info_btn = dis.Button(
            dis.ButtonStyles.GRAY,
            "Info",
            "🌐",
            custom_id=f"v_id{video_id}",
        )
        delete_msg_btn = dis.Button(
            dis.ButtonStyles.RED,
            emoji="🗑️",
            custom_id=f"delete{event.message.author.id}",
        )
        too_big = False
        if tiktok.video.size > 50000000:  # 50mb | This is Discord's limit for embeds
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

    @dis.listen(dis.events.Button)
    async def on_button_click(self, event: dis.events.Button):
        ctx = event.context
        config = await get_guild_config(ctx.guild.id)
        if ctx.custom_id.startswith("delete"):
            if dis.Permissions.MANAGE_MESSAGES in ctx.author.channel_permissions(
                ctx.channel
            ) or ctx.author.has_permission(dis.Permissions.MANAGE_MESSAGES):
                await ctx.message.delete()
            elif ctx.author.id == ctx.custom_id[6:]:
                await ctx.delete()
            else:
                await ctx.send(
                    _[config.language].gettext(
                        "You don't have the permissions to delete this message."
                    ),
                    ephemeral=True,
                )
        elif ctx.custom_id.startswith("v_id"):
            await ctx.defer(ephemeral=True)
            tiktok = await get_tiktok(int(ctx.custom_id[4:]))

            video = tiktok.video
            author = tiktok.author
            stats = tiktok.statistics
            desc = None

            if tiktok.description.cleaned != "" and tiktok.description.cleaned != None:
                desc = tiktok.description.cleaned[:256]

            embed = dis.Embed(desc, description=tiktok.share_url)

            embed.set_author(
                name=author.nickname, icon_url=author.avatar, url=author.url
            )
            embed.set_thumbnail(url=video.cover_url)
            embed.add_field(
                _[config.language].gettext("Views %s") % "👀", stats.play_count, True
            )
            embed.add_field(
                _[config.language].gettext("Likes %s") % "❤️", stats.like_count, True
            )

            embed.add_field(
                _[config.language].gettext("Comments %s") % "💬",
                stats.comment_count,
                True,
            )
            embed.add_field(
                _[config.language].gettext("Shares %s") % "🔃", stats.share_count, True
            )
            embed.add_field(
                _[config.language].gettext("Downloads %s") % "📥",
                stats.download_count,
                True,
            )

            embed.add_field(_[config.language].gettext("Created"), tiktok.created, True)
            download_btn = dis.Button(
                dis.ButtonStyles.URL,
                _[config.language].gettext("Download"),
                url=video.download_url,
            )
            if len(tiktok.description.tags) > 0:
                tags = " ".join(
                    [
                        f"[`#{tag}`](http://tiktok.com/tag/{tag})"
                        for tag in tiktok.description.tags
                    ]
                )
                if len(tags) > 1024:
                    tags = tags[:1024].rsplit(") ", 1)[0] + ") ..."

                embed.add_field(
                    _[config.language].gettext("Tags %s") % "🔖",
                    tags,
                    True,
                )

            audio_btn = dis.Button(
                dis.ButtonStyles.GRAY,
                _[config.language].gettext("Audio"),
                emoji="🎵",
                custom_id=f"m_id{tiktok.id}",
            )

            await ctx.send(embed=embed, components=[download_btn, audio_btn])
            return

        elif ctx.custom_id.startswith("m_id"):  # TODO: Use aweme instead of music
            await ctx.defer(ephemeral=True)

            try:
                tiktok = await get_tiktok(int(ctx.custom_id[4:]))
            except Exception as e:
                await ctx.send(
                    _[config.language].gettext(
                        "It seems this audio is deleted or taken down."
                    )
                )
                print(f"Error: {e}")
                return

            music = tiktok.music
            embed = dis.Embed(
                title=music.title,
                url="https://www.tiktok.com/music/id-" + str(music.id),
            )

            if extra_music_data := await get_music_data(music.id):
                video_count = extra_music_data["musicInfo"]["stats"]["videoCount"]
                embed.add_field(
                    name=_[config.language].gettext("Video Count %s") % "📱",
                    value=video_count,
                    inline=False,
                )

            embed.set_author(
                name=music.owner_nickname,
                url=music.owner_url,
                icon_url=music.avatar_url,
            )
            embed.set_thumbnail(url=music.cover_url)

            await ctx.send(
                embed=embed,
                components=dis.Button(
                    dis.ButtonStyles.URL,
                    url=music.play_url,
                    label=_[config.language].gettext("Download"),
                ),
            )


def setup(bot: dis.Snake):
    TikTok(bot)
