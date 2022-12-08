from discord    import (
    ApplicationContext,
    Cog,
    Message,
    Option,
    SlashCommandGroup,
    Thread
)
from discord.enums  import ChannelType, SlashCommandOptionType
from typing         import TYPE_CHECKING

from classes.ui.jobsUI  import *
from utils              import *

if TYPE_CHECKING:
    from classes.bot import KinoKi
    from classes.guild import GuildData
######################################################################
class JobListener(Cog):

    def __init__(self, bot: "KinoKi"):

        self.bot: "KinoKi" = bot

######################################################################
    @Cog.listener("on_thread_create")
    async def crosspost(self, thread: Thread) -> None:

        jobs_data = self.get_guild(thread.guild.id).job_postings

        if thread.parent not in jobs_data.source_channels:
            return

        if not thread.applied_tags:
            return

        role_list = []

        for tag in thread.applied_tags:
            for role in thread.guild.roles:
                if tag.name == role.name:
                    role_list.append(role)

            for job_tag in jobs_data.tags:
                if job_tag.name == tag.name:
                    for i in job_tag.roles:
                        role_list.append(i)

        string_mentions = [r.mention for r in role_list]
        mention_string = " | ".join(string_mentions)
        thread_message = await thread.fetch_message(thread.id)

        summary = (
            f">>> **New Post in {thread.parent.mention}**\n"
            f"{thread.mention}\n"
            f"{mention_string}\n"
            f"{thread.jump_url}"
        )

        for channel in jobs_data.post_channels:
            await channel.send(summary)

        return

######################################################################

    postings = SlashCommandGroup(
        name="crossposting",
        description="Job Crossposting Commands"
    )

######################################################################
    @postings.command(
        name="status",
        description="Job Crosspost Module Status and Configuration"
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

        found = jobs_data.tag_parent(tag_string)
        if found is None:
            error = SourceTagNotFound()
            await ctx.respond(embed=error, ephemeral=True)
            return

        role_check, tags = jobs_data.validate_role(map_role)
        if role_check:
            confirm = make_embed(
                title="Role Already Mapped",
                description=jobs_data.role_status(map_role),
                timestamp=False
            )
            view = ConfirmCancelView(ctx.user)

            await ctx.respond(embed=confirm, view=view)
            await view.wait()

            if not view.complete or view.value is False:
                return

        jobs_data.map_tag(tag_string, map_role)

        success = make_embed(
            title="Success!",
            description=jobs_data.role_status(map_role),
            timestamp=True
        )
        view = CloseMessageView(ctx.user)

        await ctx.respond(embed=success, view=view)
        await view.wait()

        return

######################################################################
    @postings.command(
        name="remove_map",
        description="Remove a ForumChannel tag/role ping relationship."
    )
    async def postings_remove_map(
        self,
        ctx: ApplicationContext,
        tag_string: Option(
            SlashCommandOptionType.string,
            name="forum_tag",
            description="The name of the forum tag that is mapped.",
            max_length=20,
            required=True
        ),
        tagged_role: Option(
            SlashCommandOptionType.role,
            name="role",
            description="The role that is mentioned when the tag is used.",
            required=True
        )
    ) -> None:

        guild_data = self.get_guild(ctx.guild_id)
        jobs_data = guild_data.job_postings

        tag = jobs_data.get_tag(tag_string)
        if tag is None:
            error = TagNotMapped()
            await ctx.respond(embed=error, ephemeral=True)
            return

        role_found = tagged_role in tag.roles
        if not role_found:
            error = RoleNotMapped(tag_string)
            await ctx.respond(embed=error, ephemeral=True)
            return

        tag.remove_role(tagged_role)

        tag_emoji = jobs_data.find_tag_emoji(tag)
        success = make_embed(
            title="Success!",
            description=(
                f"{tagged_role.mention} will no longer be pinged "
                f"for crossposts from ForumTag: {tag_emoji} `{tag.name}`."
            ),
            timestamp=True
        )
        view = CloseMessageView(ctx.user)

        await ctx.respond(embed=success, view=view)
        await view.wait()

        return

######################################################################
    @postings.command(
        name="map_status",
        description="View all roles mapped to a specific tag or role."
    )
    async def postings_map_status(
        self,
        ctx: ApplicationContext,
        tag_string: Option(
            SlashCommandOptionType.string,
            name="forum_tag",
            description="The name of the forum tag to search for.",
            max_length=20,
            required=False
        ),
        role_object: Option(
            SlashCommandOptionType.role,
            name="role",
            description="The role to search for mappings of.",
            required=False
        )
    ) -> None:

        guild_data = self.get_guild(ctx.guild_id)
        jobs_data = guild_data.job_postings

        if tag_string is None and role_object is None:
            await jobs_data.view_all_mappings(ctx.interaction)
            return

        else:
            tag = jobs_data.get_tag(tag_string)
            found, tag_list = jobs_data.validate_role(role_object)

            if tag is None and tag_string is not None:
                error = TagNotMapped()
                await ctx.respond(embed=error, ephemeral=True)
                return

            if not found and role_object is not None:
                error = RoleNotMapped()
                await ctx.respond(embed=error, ephemeral=True)
                return

            if role_object is None:
                status = tag.status()

            elif tag_string is None:
                status = make_embed(
                    title="Role Mapping Status",
                    description=jobs_data.role_status(role_object),  # type: ignore
                    timestamp=False
                )

            else:
                if tag in tag_list:
                    title = "Confirmed"
                    description = (
                        f"{tag.name} **IS** currently mapped to "
                        f"{role_object.mention}.\n\n"
                        
                        f"When the tag is used in {tag.channel.mention}, "
                        "that role will be pinged."
                    )

                else:
                    title = "Invalid Pair"
                    description = (
                        f"{tag.name} **IS NOT** currently mapped to "
                        f"{role_object.mention}.\n\n"

                        "Use `/crosspost map_role` to create a link."
                    )

                status = make_embed(
                    title=title,
                    description=description,
                    timestamp=False
                )

            view = CloseMessageView(ctx.user)

            await ctx.respond(embed=status, view=view)
            await view.wait()

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
