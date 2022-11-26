from discord    import (
    Cog,
    Option,
    SlashCommandGroup
)
from discord.enums  import ChannelType, SlashCommandOptionType
from typing         import TYPE_CHECKING

from errors     import ChannelTypeError

if TYPE_CHECKING:
    from discord    import (
        ApplicationContext,
        Bot,
        Message
    )
######################################################################
class JobListener(Cog):

    def __init__(self, bot: Bot):

        self.bot: Bot = bot

######################################################################
    @Cog.listener("on_message")
    async def crosspost(self, message: Message):

        pass

######################################################################

    postings = SlashCommandGroup(
        name="postings",
        description="Job Crossposting Configuration"
    )

######################################################################
    @postings.command(
        name="source",
        description="Configure the source channel for crossposting jobs."
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


######################################################################
def setup(bot: Bot) -> None:
    """Setup function required by commands.Cog superclass
    to integrate module into the bot. Basically magic.

    Args:
        bot: The Bot... duh. Yes, I'm putting this every time.

    Returns:
        None

    """

    bot.add_cog(JobListener(bot))

######################################################################
