from discord    import (
    ApplicationContext,
    Cog,
    ComponentType,
    ForumChannel,
    Message,
    Option,
    option,
    SlashCommandGroup
)
from discord.enums  import ChannelType, SlashCommandOptionType
from discord.ui     import Select
from typing         import TYPE_CHECKING

from utils          import ChannelTypeError, CloseMessageView

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
        name="crosspostings",
        description="Job Crossposting Configuration"
    )

######################################################################
    @postings.command(
        name="status",
        description="Job Crosspost Module Status and Settings"
    )
    async def postings_status(self, ctx: ApplicationContext) -> None:

        guild_data = self.get_guild(ctx.guild_id)

        await guild_data.job_postings.menu_add_source_channel(ctx.interaction)
        # status = guild_data.job_postings.status_all()
        # view = CloseMessageView(ctx.user)
        #
        # await ctx.respond(embed=status, view=view)
        # await view.wait()

        return

######################################################################
    @postings.command(
        name="add_source",
        description="Configure the source channel(s) for crossposting jobs."
    )
    async def postings_source(
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

######################################################################
    # @postings.command(
    #     name="remove_source",
    #     description=
    # )
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