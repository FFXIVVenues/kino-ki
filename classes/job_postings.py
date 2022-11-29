from __future__ import annotations

from discord    import (
    ApplicationContext,
    ChannelType,
    EmbedField,
)
from typing     import (
    TYPE_CHECKING,
    List,
    Optional,
    Type,
    TypeVar
)

from classes.ui.jobsUI  import *
from utils              import (
    NS,
    CloseMessageView,
    ConfirmCancelView,
    SeparatorField,
    convert_db_list,
    database as db,
    make_embed,
)

from utils.errors       import *

if TYPE_CHECKING:
    from discord        import (
        Embed,
        ForumChannel,
        Interaction,
        TextChannel
    )
    from discord.abc    import GuildChannel

    from classes.bot    import KinoKi
    from classes.guild  import GuildData
######################################################################

__all__ = ("JobPostings", )

JP = TypeVar("JP", bound="JobPostings")

######################################################################
class JobPostings:
    """Represents a collection of data pertaining to job posting
    functions.
    """

    __slots__ = (
        "guild",
        "source_channels",
        "post_channels"
    )

######################################################################
    def __init__(
        self,
        guild: GuildData,
        source_channels: List[ForumChannel],
        post_channels: List[TextChannel]
    ):
        self.guild: GuildData = guild

        self.source_channels: List[ForumChannel] = source_channels
        self.post_channels: List[TextChannel] = post_channels

######################################################################
    @classmethod
    async def load(cls: Type[JP], *, bot: KinoKi, guild: GuildData) -> JP:

        source_channels: List[ForumChannel] = []
        post_channels: List[TextChannel] = []
        missing_channels: List[int] = []

        # Channel type validation is done when the data is stored, so any
        # channels returned during this load will be of the proper type.
        # Unless they're deleted, in which case the ID is ignored and will
        # be overwritten in the database on the next self.update() call.

        c = db.connection.cursor()
        c.execute(
            "SELECT * FROM job_postings WHERE guild_id = %s",
            (guild.parent.id, )
        )

        data = c.fetchall()[0]
        c.close()

        source_ids = [int(i) for i in convert_db_list(data[1])]
        post_ids = [int(i) for i in convert_db_list(data[2])]

        for channel_id in source_ids:
            source_channel = guild.parent.get_channel(channel_id)
            if source_channel is None:
                try:
                    source_channel = await bot.fetch_channel(channel_id)
                except:
                    pass
                else:
                    source_channels.append(source_channel)  # type: ignore
            else:
                source_channels.append(source_channel)  # type: ignore

        for channel_id in post_ids:
            post_channel = guild.parent.get_channel(channel_id)
            if post_channel is None:
                try:
                    post_channel = await bot.fetch_channel(channel_id)
                except:
                    pass
                else:
                    post_channels.append(post_channel)  # type: ignore
            else:
                post_channels.append(post_channel)  # type: ignore

        return cls(
            guild=guild,
            source_channels=source_channels,
            post_channels=post_channels
        )

######################################################################
    def status_all(self) -> Embed:

        fields = [
            EmbedField("__Source Channel(s)__", self.list_sources(), True),
            EmbedField("__Post Channel(s)__", self.list_destinations(), True),
            SeparatorField(6),
            EmbedField("__Posting Stats__", "*(Coming Soon!)*", False),
            SeparatorField(6),
        ]

        return make_embed(
            title="Job Crossposting Module",
            fields=fields
        )

######################################################################
    def source_channel_status(self) -> Embed:

        return make_embed(
            title="Job Cross-posting Source Channel(s)",
            description=(
                "==============================\n"
                f"{self.list_sources()}"
            )
        )

######################################################################
    def post_channel_status(self) -> Embed:

        return make_embed(
            title="Job Cross-posting Post Channel(s)",
            description=(
                "==============================\n"
                f"{self.list_destinations()}"
            )
        )

######################################################################
    def list_sources(self) -> str:

        if self.source_channels:
            current_sources = "\n- ".join(
                [c.mention for c in self.source_channels]
            )
            return f"- {current_sources}"

        return NS

######################################################################
    def list_destinations(self) -> str:

        if self.post_channels:
            post_channels = "\n- ".join(
                [ch.mention for ch in self.post_channels]
            )
            return f"- {post_channels}"

        return NS

######################################################################
    async def menu_add_source_channel(self, interaction: Interaction) -> None:

        prompt = make_embed(
            title="Select New Source Channel",
            description="Pick a channel to listen in on for job cross-posts.",
            timestamp=False
        )

        channel_list = [
            channel for channel in interaction.guild.channels
            if channel.type is ChannelType.forum
        ]
        view = ChannelSelectView(interaction.user, channel_list)

        await interaction.response.send_message(embed=prompt, view=view)
        await view.wait()

        if not view.complete:
            return

        if view.value in self.source_channels:
            embed = ChannelAlreadyExistsError(view.value.mention, "Source")
            view = None
            ephemeral = True

        else:
            self.update(source_channel=view.value)
            ephemeral = False

            embed = self.source_channel_status()
            view = CloseMessageView(interaction.user)

        await interaction.followup.send(
            embed=embed, view=view, ephemeral=ephemeral
        )

        return

######################################################################
    async def menu_remove_source_channel(self, interaction: Interaction) -> None:

        prompt = make_embed(
            title="Select Source Channel to Remove",
            description="Pick a channel to remove from job cross-post listening.",
            timestamp=False
        )
        view = ChannelSelectView(interaction.user, self.source_channels)

        await interaction.response.send_message(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        for channel in self.source_channels:
            if channel == view.value:
                self.source_channels.remove(channel)
                break

        self.update()

        status = self.source_channel_status()
        view = CloseMessageView(interaction.user)

        await interaction.followup.send(embed=status, view=view)
        await view.wait()

        return

######################################################################
    async def menu_add_post_channel(self, interaction: Interaction) -> None:

        prompt = make_embed(
            title="Select New Post Channel",
            description=(
                "Pick a channel to register as a destination for job "
                "cross-posts."
            ),
            timestamp=False
        )

        channel_list = [
            c for c in interaction.guild.channels
            if c.type is ChannelType.text
        ]
        view = ChannelSelectView(interaction.user, channel_list)

        await interaction.response.send_message(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        self.update(post_channel=view.value)

        status = self.post_channel_status()
        view = CloseMessageView(interaction.user)

        await interaction.followup.send(embed=status, view=view)
        await view.wait()

        return

######################################################################
    async def menu_remove_post_channel(self, interaction: Interaction) -> None:

        prompt = make_embed(
            title="Select Post Channel to Remove",
            description="Pick a channel to remove from job cross-post postings.",
            timestamp=False
        )
        view = ChannelSelectView(interaction.user, self.post_channels)

        await interaction.response.send_message(embed=prompt, view=view)
        await view.wait()

        if not view.complete or view.value is False:
            return

        for channel in self.post_channels:
            if channel == view.value:
                self.post_channels.remove(channel)
                break

        self.update()

        status = self.source_channel_status()
        view = CloseMessageView(interaction.user)

        await interaction.followup.send(embed=status, view=view)
        await view.wait()

        return

######################################################################
    async def slash_add_source_channel(
        self, ctx: ApplicationContext, channel: ForumChannel
    ) -> None:

        if not self.source_channels:
            self.update(source_channel=channel)
        else:
            if channel in self.source_channels:
                error = ChannelAlreadyExistsError(channel.mention, "Source")
                await ctx.respond(embed=error, ephemeral=True)
                return

            confirm = make_embed(
                title="Confirm Job Source Channel Add",
                description=(
                    "There are currently one or more channels already "
                    "configured as the source(s) for job cross-postings. "
                    "\n\n"
                    "Current Job Cross-posting Source Channels:\n"
                    f"{self.list_sources()}\n\n"
                    
                    "==============================\n"
                    f"Please confirm you wish you add "
                    f"{channel.mention} to this list."
                )
            )

            view = ConfirmCancelView(ctx.user, close_on_interact=True)

            await ctx.respond(embed=confirm, view=view)
            await view.wait()

            if not view.complete or view.value is False:
                return

            self.update(source_channel=channel)

        status = self.source_channel_status()
        view = CloseMessageView(ctx.user)

        await ctx.respond(embed=status, view=view)
        await view.wait()

        return

######################################################################
    async def slash_remove_source_channel(
        self, ctx: ApplicationContext, channel: GuildChannel
    ) -> None:

        if channel not in self.source_channels:
            error = ChannelNotFound(channel.mention, "Job Source")
            await ctx.respond(embed=error, ephemeral=True)
            return

        confirm = make_embed(
            title="Remove Job Cross-posting Source Channel?",
            description=(
                f"Job postings in {channel.mention} will no longer be "
                "cross-posted."
            )
        )
        view = ConfirmCancelView(ctx.user, close_on_interact=True)

        await ctx.respond(embed=confirm, view=view)
        await view.wait()

        if view.value is True:
            self.source_channels.remove(channel)  # type: ignore
            self.update()

            status = self.source_channel_status()
            view = CloseMessageView(ctx.user)

            await ctx.respond(embed=status, view=view)
            await view.wait()

        return

######################################################################
    async def slash_add_post_channel(
        self, ctx: ApplicationContext, channel: TextChannel
    ) -> None:

        if not self.post_channels:
            self.update(post_channel=channel)
        else:
            if channel in self.post_channels:
                error = ChannelAlreadyExistsError(channel.mention, "Destination")
                await ctx.respond(embed=error, ephemeral=True)
                return

            confirm = make_embed(
                title="Confirm Job Cross-post Destination Channel Add",
                description=(
                    "There are currently one or more channels already "
                    "configured as the destinations(s) for job "
                    "cross-postings. \n\n"
                    
                    "Current Job Cross-posting Destination Channels:\n"
                    f"{self.list_destinations()}\n\n"

                    "==============================\n"
                    f"Please confirm you wish you add "
                    f"{channel.mention} to this list."
                )
            )

            view = ConfirmCancelView(ctx.user, close_on_interact=True)

            await ctx.respond(embed=confirm, view=view)
            await view.wait()

            if not view.complete or view.value is False:
                return

            self.update(post_channel=channel)

        status = self.post_channel_status()
        view = CloseMessageView(ctx.user)

        await ctx.respond(embed=status, view=view)
        await view.wait()

        return

######################################################################
    async def slash_remove_post_channel(
        self, ctx: ApplicationContext, channel: GuildChannel
    ) -> None:

        if channel not in self.post_channels:
            error = ChannelNotFound(channel.mention, "Job Post Destination")
            await ctx.respond(embed=error, ephemeral=True)
            return

        confirm = make_embed(
            title="Remove Job Cross-posting Destination Channel?",
            description=(
                f"Job postings will no longer be cross-posted to "
                f"{channel.mention} ."
            )
        )
        view = ConfirmCancelView(ctx.user, close_on_interact=True)

        await ctx.respond(embed=confirm, view=view)
        await view.wait()

        if view.value is True:
            self.post_channels.remove(channel)  # type: ignore
            self.update()

            status = self.post_channel_status()
            view = CloseMessageView(ctx.user)

            await ctx.respond(embed=status, view=view)
            await view.wait()

        return

######################################################################
    def update(
        self,
        source_channel: Optional[ForumChannel] = None,
        post_channel: Optional[TextChannel] = None
    ) -> None:

        if source_channel is not None:
            self.source_channels.append(source_channel)
        if post_channel is not None:
            self.post_channels.append(post_channel)

        source_ids = [channel.id for channel in self.source_channels]
        post_ids = [channel.id for channel in self.post_channels]

        c = db.connection.cursor()
        c.execute(
            "UPDATE job_postings SET sources = %s, destinations = %s "
            "WHERE guild_id = %s",
            (source_ids, post_ids, self.guild.parent.id)
        )

        db.connection.commit()
        c.close()

        return

######################################################################
