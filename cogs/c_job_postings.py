from discord    import (
    ApplicationContext,
    Cog,
    Message,
    Option,
    SlashCommandGroup
)
from discord.enums  import ChannelType, SlashCommandOptionType
from typing         import TYPE_CHECKING

from classes.ui.jobsUI  import *
from utils.errors       import *

if TYPE_CHECKING:

    from classes.bot import KinoKi
    from classes.guild import GuildData
######################################################################
class JobListener(Cog):

    def __init__(self, bot: "KinoKi"):

        self.bot: "KinoKi" = bot

######################################################################
    @Cog.listener("on_message")
    async def crosspost(self, message: Message):

        pass

######################################################################

    postings = SlashCommandGroup(
        name="crossposting",
        description="Job Crossposting Configuration"
    )

######################################################################
    @postings.command(
        name="status",
        description="Job Crosspost Module Status"
    )
    async def postings_status(self, ctx: ApplicationContext) -> None:

        guild_data = self.get_guild(ctx.guild_id)

        status = guild_data.job_postings.status_all()
        view = CrosspostStatusView(ctx.user, guild_data.job_postings)

        await ctx.respond(embed=status, view=view)
        await view.wait()

        return

######################################################################
    @postings.command(
        name="add_source",
        description="Add a source channel for crossposting jobs."
    )
    async def postings_source_add(
            self,
            ctx: ApplicationContext,
            channel: Option(
                SlashCommandOptionType.channel,
                name="source_channel",
                description="Job posting source channel. Must be a ForumChannel.",
                required=True
            )
    ) -> None:

        if not channel.type == ChannelType.forum:
            error = ChannelTypeError("Forum Channel")
            await ctx.respond(embed=error, ephemeral=True)
            return

        guild_data = self.get_guild(ctx.guild_id)
        await guild_data.job_postings.slash_add_source_channel(ctx, channel)

        return

######################################################################
    @postings.command(
        name="remove_source",
        description="Remove a source channel for crossposting jobs."
    )
    async def postings_source_remove(
            self,
            ctx: ApplicationContext,
            channel: Option(
                SlashCommandOptionType.channel,
                name="channel_to_remove",
                description="Channel to remove as a cross-posting source.",
                required=True
            )
    ) -> None:

        guild_data = self.get_guild(ctx.guild_id)
        await guild_data.job_postings.slash_remove_source_channel(ctx, channel)

        return

######################################################################
    @postings.command(
        name="add_destination",
        description="Add a destination channel for crossposting jobs."
    )
    async def postings_destination_add(
        self,
        ctx: ApplicationContext,
        channel: Option(
            SlashCommandOptionType.channel,
            name="post_channel",
            description=(
                "Job posting destination channel. Must be a TextChannel."
            ),
            required=True
        )
    ) -> None:

        if not channel.type == ChannelType.text:
            error = ChannelTypeError("Text Channel")
            await ctx.respond(embed=error, ephemeral=True)
            return

        guild_data = self.get_guild(ctx.guild_id)
        await guild_data.job_postings.slash_add_post_channel(ctx, channel)

        return

######################################################################
    @postings.command(
        name="remove_destination",
        description="Remove a destination channel for crossposting jobs."
    )
    async def postings_source_remove(
            self,
            ctx: ApplicationContext,
            channel: Option(
                SlashCommandOptionType.channel,
                name="channel_to_remove",
                description="Channel to remove as a cross-posting destination.",
                required=True
            )
    ) -> None:

        guild_data = self.get_guild(ctx.guild_id)
        await guild_data.job_postings.slash_remove_post_channel(ctx, channel)

        return

######################################################################
    def get_guild(self, guild_id: int) -> "GuildData":

        for guild in self.bot.k_guilds:
            if guild.parent.id == guild_id:
                return guild

######################################################################
def setup(bot: "KinoKi") -> None:
    """Setup function required by commands.Cog superclass
    to integrate module into the bot. Basically magic.

    Args:
        bot: The Bot... duh. Yes, I'm putting this every time.

    """

    bot.add_cog(JobListener(bot))

######################################################################
