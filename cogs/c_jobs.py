from discord    import (
    ApplicationContext,
    ChannelType,
    Cog,
    Colour,
    default_permissions,
    ForumChannel,
    Option,
    Permissions,
    SlashCommandGroup,
    SlashCommandOptionType,
    Thread
)
from typing     import TYPE_CHECKING

from ui         import *
from utilities  import *

if TYPE_CHECKING:
    from classes.bot    import KinoKi
    from classes.guild  import GuildData
####################################################################################################
class JobListeners(Cog):

    def __init__(self, bot: "KinoKi"):

        self.bot: "KinoKi" = bot

####################################################################################################

####################################################################################################

    postings = SlashCommandGroup(
        name="jobs",
        description="Job Crossposting Commands"
    )

    sumi = SlashCommandGroup(
        name="hey_sumi",
        description="Click me..."
    )

####################################################################################################
    @sumi.command(
        name="nou",
        description="Click me..."
    )
    async def nou(self, ctx):

        embed = make_embed(
            title="NO U",
            description="nounounounounounounounounounounounounounounounounounounounounou",
            author_name="No... U",
            author_icon="https://cdn.discordapp.com/attachments/957656105092272208/1075103689712340992/nou-no.gif",
            footer_text="Nuh uh. YOUYOUYOU!",
            footer_icon="https://cdn.discordapp.com/attachments/957656105092272208/1075104030721839196/images_1.png",
            thumbnail_url="https://cdn.discordapp.com/attachments/957656105092272208/1075103690060476416/no-u-turn.jpg",
            image_url="https://cdn.discordapp.com/attachments/957656105092272208/1075104193641205821/no-u-reverse-card.gif",
            timestamp=False
        )

        await ctx.respond(embed=embed)

####################################################################################################
    @postings.command(
        name="status",
        description="Job Crosspost Module Status and Configuration"
    )
    async def postings_status(self, ctx: ApplicationContext) -> None:

        guild_data = self.get_guild(ctx.guild_id)
        status = guild_data.job_postings.status_all()

        await ctx.respond(embed=status)

        return

####################################################################################################
    @postings.command(
        name="add_source",
        description="Add a source forum channel for crossposting jobs."
    )
    async def postings_add_source(
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
        await guild_data.job_postings.add_source_channel(ctx.interaction, channel)

        return

####################################################################################################
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
                "Job posting destination channel to add. Must be a TextChannel."
            ),
            required=True
        )
    ) -> None:

        if not channel.type == ChannelType.text:
            error = ChannelTypeError("Text Channel")
            await ctx.respond(embed=error, ephemeral=True)
            return

        guild_data = self.get_guild(ctx.guild_id)
        await guild_data.job_postings.add_post_channel(ctx.interaction, channel)

        return

####################################################################################################
    @postings.command(
        name="remove_channel",
        description="Remove a post or destination channel for crossposting jobs."
    )
    async def postings_source_remove(
        self,
        ctx: ApplicationContext,
        channel: Option(
            SlashCommandOptionType.channel,
            name="channel_to_remove",
            description="Channel to remove as a cross-posting resource.",
            required=True
        )
    ) -> None:

        guild_data = self.get_guild(ctx.guild_id)
        await guild_data.job_postings.remove_channel(ctx.interaction, channel)

        return

####################################################################################################
    @postings.command(
        name="map_role",
        description="Map a ForumChannel tag to a server role for pinging."
    )
    async def postings_map_role(
        self,
        ctx: ApplicationContext,
        tag_string: Option(
            SlashCommandOptionType.string,
            name="forum_tag",
            description="The name of the forum tag to listen for.",
            max_length=20,
            required=True
        ),
        map_role: Option(
            SlashCommandOptionType.role,
            name="role",
            description="The role to mention when the tag is used.",
            required=True
        )
    ) -> None:

        guild_data = self.get_guild(ctx.guild_id)
        jobs_data = guild_data.job_postings

        parent_channel = jobs_data.get_tag_parent_channel(tag_string)
        parent_tag = jobs_data.get_parent_tag(tag_string)
        if parent_channel is None or parent_tag is None:
            error = SourceTagNotFound()
            await ctx.respond(embed=error, ephemeral=True)
            return

        map_check, _ = jobs_data.check_for_role_mapping(map_role, parent_tag)

        # If map_check is false, it means the pair wasn't found and can be created
        if not map_check:
            jobs_data.map_tag(parent_tag, map_role)
            confirm = make_embed(
                title="Success!",
                description=jobs_data.role_status(map_role),
                timestamp=True
            )
            view = CloseMessageView(ctx.user)

            await ctx.respond(embed=confirm, view=view)
            await view.wait()

            return

        # Otherwise we ask if the user wants to remove the pairing.
        # (If map_check is true, then there should always be data in tags)
        await jobs_data.remove_mapping(ctx.interaction, parent_tag, map_role)

        return

####################################################################################################
    @postings.command(
        name="map_status",
        description="View all roles mapped to a specific tag or role."
    )
    async def postings_map_status(self, ctx: ApplicationContext) -> None:

        guild_data = self.get_guild(ctx.guild_id)
        jobs_data = guild_data.job_postings

        await jobs_data.view_all_mappings(ctx.interaction)
        return

####################################################################################################
    def get_guild(self, guild_id: int) -> "GuildData":

        for guild in self.bot.k_guilds:
            if guild.parent.id == guild_id:
                return guild

####################################################################################################
def setup(bot: "KinoKi") -> None:
    """Setup function required by commands.Cog superclass
    to integrate module into the bot. Basically magic.

    Args:
        bot: The Bot... duh. Yes, I'm putting this every time.

    """

    bot.add_cog(JobListeners(bot))

####################################################################################################