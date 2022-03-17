""" General Scale """

import subprocess
from datetime import datetime, timedelta
from collections import Counter
import dis_snek as dis
from tiktoker.utils import (
    add_opted_out,
    get_all_usage_data,
    get_tiktok,
    remove_opted_out,
    remove_usage_data,
    get_guild_config,
    get_opted_out,
)
from tiktoker.utils.translate import load_lang, language_names as lang_names
from dis_snek.ext.paginators import Paginator

_ = load_lang("general")


class General(dis.Scale):
    """General commands and stuff"""

    def __init__(self, bot: dis.Snake):
        self.bot = bot

    @dis.slash_command("help", "All the help you need")
    async def help(self, ctx: dis.InteractionContext):
        config = await get_guild_config(ctx.guild.id)
        embeds = [
            dis.Embed(
                title=_[config.language].gettext("What is TikToker?"),
                description=_[config.language].gettext(
                    "Tiktoker is a bot that allows you to send playable TikTok videos to your Discord server."
                ),
                color="#00FFF0",
                fields=[
                    dis.EmbedField(
                        _[config.language].gettext("Help Menu"),
                        _[config.language].gettext(
                            "Click the arrow buttons below to navigate the help menu."
                        ),
                    ).to_dict(),
                ],
            ),
            dis.Embed(
                _[config.language].gettext("Server Configuration"),
                _[config.language].gettext(
                    "You may view the configuration of your server with `/config`.\nTo edit the config use, `/config <option>`.\nExample: `/config delete_origin:True`"
                ),
                color="#00FFF0",
                fields=[
                    dis.EmbedField(
                        "Auto Embed",
                        _[config.language].gettext(
                            "If enabled, the bot will automatically embed the Tiktok links."
                        ),
                    ).to_dict(),
                    dis.EmbedField(
                        "Delete Origin",
                        _[config.language].gettext(
                            "If enabled and _Auto Embed_ is enabled, the bot will delete the origin message containing the TikTok link."
                        ),
                    ).to_dict(),
                    dis.EmbedField(
                        "Suppress Origin Embed",
                        _[config.language].gettext(
                            "If enabled, the origin embed will be removed."
                        ),
                    ).to_dict(),
                    dis.EmbedField(
                        "Language",
                        _[config.language].gettext("Set the language of the bot. "),
                    ).to_dict(),
                ],
            ),
            dis.Embed(
                _[config.language].gettext("Commands"),
                _[config.language].gettext(
                    "Here are some commands to interact with the bot."
                ),
                color="#00FFF0",
                fields=[
                    dis.EmbedField(
                        "Convert 📸",
                        _[config.language].gettext(
                            "To use, right-click a message, go to `Apps > Convert %s`. Useful for when _Auto Embed_ is disabled in your server's configuration."
                        )
                        % "📸",
                    ).to_dict(),
                    dis.EmbedField(
                        "/tiktok",
                        _[config.language].gettext(
                            "A slash command that takes a TikTok link and returns the video. Useful for when _Auto Embed_ is disabled in your server's configuration."
                        ),
                    ).to_dict(),
                    dis.EmbedField(
                        "/info",
                        _[config.language].gettext(
                            "Provides some general information and statistics about TikToker."
                        ),
                    ).to_dict(),
                ],
            ),
        ]

        paginator = Paginator.create_from_embeds(self.bot, *embeds, timeout=30)
        paginator.default_button_color = dis.ButtonStyles.GRAY
        paginator.first_button_emoji = "<:tiktoker_first_arrow:951169872849670244>"
        paginator.last_button_emoji = "<:tiktoker_last_arrow:951169872841277461>"
        paginator.next_button_emoji = "<:tiktoker_next_arrow:951169872749019226>"
        paginator.back_button_emoji = "<:tiktoker_back_arrow:951169873306853436>"
        paginator.show_select_menu = True
        paginator.wrong_user_message = _[config.language].gettext(
            "This menu is not for you"
        )

        await paginator.send(ctx)

    @dis.slash_command(
        name="privacy",
        description="Inform yourself of some of the data we collect.",
        sub_cmd_name="policy",
        sub_cmd_description="Review our Privacy Policy.",
    )
    async def privacy_policy(self, ctx: dis.InteractionContext):
        await ctx.send("<https://tiktoker.win/privacy>")  # TODO: Make a privacy policy

    @dis.slash_command(
        name="privacy",
        description="Inform yourself of some of the data we collect.",
        group_name="usage",
        sub_cmd_name="data",
        sub_cmd_description="Choose what we can collect about you.",
    )
    @dis.slash_option(
        "collect",
        "Save usage data?",
        dis.OptionTypes.STRING,
        choices=[
            dis.SlashCommandChoice("Yes (collect data)", "yes"),
            dis.SlashCommandChoice("No (do not collect)", "no"),
            dis.SlashCommandChoice("Delete (delete server usage data)", "delete"),
        ],
    )
    async def privacy_options(self, ctx: dis.InteractionContext, collect: str = None):
        await ctx.defer(True)
        config = await get_guild_config(ctx.guild.id)

        if collect is None:
            state = (
                _[config.language].gettext("Opted-out")
                if await get_opted_out(ctx.author.id)
                else _[config.language].gettext("Opted-in")
            )
            await ctx.send(
                _[config.language].gettext(
                    "You are currently: %s \n\n**We take your privacy seriously.**\nYour data is not public. Usage data provides statistics like total videos converted and total users. Please consider sharing your usage data with us to help improve the bot. View the help command for more information on how we handle your privacy."
                )
                % state
            )
            return

        if collect == "yes":
            await ctx.send(
                _[config.language].gettext(
                    "Thank you for sharing your usage data. It will go towards improving the bot."
                )
            )
            await remove_opted_out(ctx.author.id)

        elif collect == "no":
            await ctx.send(
                _[config.language].gettext(
                    "You have opted out of usage data collection. Thank you for your time."
                )
            )
            await add_opted_out(ctx.author.id)

        elif collect == "delete":
            await ctx.send(
                _[config.language].gettext(
                    "Your usage data for this server has been deleted."
                )
            )
            await remove_usage_data(ctx.guild.id, ctx.author.id)

    @dis.slash_command(
        "config",
        "Configure the bot for your server.",
    )
    @dis.slash_option(
        "auto_embed", "Toggle auto embedding of TikTok links.", dis.OptionTypes.BOOLEAN
    )
    @dis.slash_option(
        "delete_origin",
        "Toggle the deletion of the origin message. (When auto_embed True)",
        dis.OptionTypes.BOOLEAN,
    )
    @dis.slash_option(
        "suppress_origin_embed",
        "Toggle suppression of the origin message embed.",
        dis.OptionTypes.BOOLEAN,
    )
    # languages=["en", "es", "pl", "vi", "de"]

    @dis.slash_option(
        "language",
        "The language of the bot.",
        dis.OptionTypes.STRING,
        choices=[
            dis.SlashCommandChoice(value, key) for key, value in lang_names.items()
        ],
    )
    async def setup_config(
        self,
        ctx: dis.InteractionContext,
        auto_embed: bool = None,
        delete_origin: bool = None,
        suppress_origin_embed: bool = None,
        language: str = None,
    ):
        """
        Sets up the config for the guild.
        """
        if not ctx.author.has_permission(
            dis.Permissions.MANAGE_GUILD | dis.Permissions.ADMINISTRATOR
        ):
            await ctx.send(
                _[config.language].gettext(
                    "You do not have permission to use this command. Reason: `Missing Manage Server Permission`"
                ),
                ephemeral=True,
            )
            return

        guild_id = ctx.guild.id
        await ctx.defer()
        config = await get_guild_config(guild_id)
        if (
            auto_embed is None
            and delete_origin is None
            and suppress_origin_embed is None
            and language is None
        ):
            embed = dis.Embed(
                _[config.language].gettext("Current Config"),
                _[config.language].gettext(
                    "To change a setting, use `/config <setting> <value>`."
                ),
            )
            embed.add_field(
                "Auto Embed", "☑️" if config.auto_embed else "❌", inline=True
            )
            embed.add_field(
                "Delete Origin", "☑️" if config.delete_origin else "❌", inline=True
            )
            embed.add_field(
                "Suppress Origin Embed",
                "☑️" if config.suppress_origin_embed else "❌",
                inline=True,
            )
            embed.add_field("Language", config.language, inline=True)
            await ctx.send(embed=embed)
            return

        if auto_embed is not None:
            config.auto_embed = auto_embed
        if delete_origin is not None:
            config.delete_origin = delete_origin
        if suppress_origin_embed is not None:
            config.suppress_origin_embed = suppress_origin_embed
        if language is not None:
            config.language = language

        await config.save()

        embed = dis.Embed(
            _[config.language].gettext("Current Config"),
            _[config.language].gettext(
                "To change a setting, use `/config <setting> <value>`."
            ),
        )
        embed.add_field("Auto Embed", "☑️" if config.auto_embed else "❌", inline=True)
        embed.add_field(
            "Delete Origin", "☑️" if config.delete_origin else "❌", inline=True
        )
        embed.add_field(
            "Suppress Origin Embed",
            "☑️" if config.suppress_origin_embed else "❌",
            inline=True,
        )
        embed.add_field("Language", config.language, inline=True)
        await ctx.send(embed=embed)

    @dis.slash_command(
        "info", "Here is some general information and statistics about TikToker."
    )
    @dis.cooldown(dis.Buckets.GUILD, 1, 10)
    async def info(self, ctx: dis.Context):
        await ctx.defer()

        config = await get_guild_config(ctx.guild.id)
        usage_data = await get_all_usage_data()

        unique_users = len(set([x.user_id for x in usage_data if x.user_id]))
        total_converted_today = len(
            [
                x
                for x in usage_data
                if x.entry_time > (datetime.now() - timedelta(days=1))
            ]
        )

        most_popular_video_id = Counter([x.video_id for x in usage_data]).most_common(
            1
        )[0][0]
        commit = (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode("utf-8")
            .strip()
        )
        repo_url = (
            subprocess.check_output(["git", "config", "--get", "remote.origin.url"])
            .decode("utf-8")
            .strip()[:-4]
            + f"/tree/{commit}"
        )
        pop_tok = await get_tiktok(
            most_popular_video_id
        )  # NOTE: pop_tok is short for most_popular_tiktok (lol)

        embed = dis.Embed(
            _[config.language].gettext("TikToker Info"),
            description=_[config.language].gettext(
                "Here is some general information and statistics about TikToker."
            ),
            color="#00FFF0",
        )
        embed.add_field(
            name=_[config.language].gettext("TikToks Converted %s") % "📷",
            value=len(usage_data),
            inline=True,
        )
        embed.add_field(
            name=_[config.language].gettext("Converted Today %s") % "🕒",
            value=total_converted_today,
            inline=True,
        )
        embed.add_field(
            name=_[config.language].gettext("Most Popular TikTok %s") % "",
            value=f"[{pop_tok.author.nickname} - {pop_tok.description.cleaned}]({pop_tok.share_url} '{pop_tok.share_url}')",
            inline=True,
        )
        embed.add_field(
            name=_[config.language].gettext("Server Count %s") % "📡",
            value=len(ctx.bot.guilds),
            inline=True,
        )
        embed.add_field(
            name=_[config.language].gettext("User Count %s") % "👤",
            value=unique_users,
            inline=True,
        )
        embed.add_field(
            name=_[config.language].gettext("Ping %s") % "🏓",
            value=f"{ctx.bot.latency * 1000:.0f}ms",
            inline=True,
        )
        embed.add_field(
            name=_[config.language].gettext("Commit Version %s") % "🔗",
            value=f"[{commit}]({repo_url})",
            inline=True,
        )

        await ctx.send(embed=embed)

    @info.error
    async def info_command_error(self, error, ctx: dis.InteractionContext):
        config = await get_guild_config(ctx.guild.id)
        if isinstance(error, dis.errors.CommandOnCooldown):
            await ctx.send(
                _[config.language].gettext(
                    "This command is on cooldown. Try again in %s seconds."
                )
                % round(error.cooldown.get_cooldown_time()),
                ephemeral=True,
            )


def setup(bot: dis.Snake):
    General(bot)
