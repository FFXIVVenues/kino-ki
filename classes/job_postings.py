from __future__ import annotations

from dataclasses    import dataclass
from discord        import (
    ApplicationContext,
    ChannelType,
    EmbedField
)
from discord.ext.pages  import Page, Paginator
from typing         import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Tuple,
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
        Message,
        PartialEmoji,
        Role,
        TextChannel,
        Thread
    )
    from discord.abc    import GuildChannel

    from classes.bot    import KinoKi
    from classes.guild  import GuildData
######################################################################

__all__ = ("JobPostings", )

JP = TypeVar("JP", bound="JobPostings")
JT = TypeVar("JT", bound="JobTag")

######################################################################
@dataclass
class JobTag:
    """Represents data involving a Forum Tag / Role Pairing."""

    __slots__ = (
        "channel",
        "name",
        "roles"
    )

    channel: ForumChannel
    name: str
    roles: List[Role]

######################################################################
    @classmethod
    def new(
        cls: Type[JT],
        *,
        guild_id: int,
        channel: ForumChannel,
        name: str,
        role: Role
    ) -> JT:

        c = db.connection.cursor()
        c.execute(
            "INSERT INTO job_tags (guild_id, channel_id, name, role_ids) "
            "VALUES (%s, %s, %s, %s)",
            (guild_id, channel.id, name, [role.id])
        )

        db.connection.commit()
        c.close()

        return cls(
            channel=channel,
            name=name,
            roles=[role]
        )

######################################################################
    def status(self) -> Embed:

        roles = "\n- ".join([role.mention for role in self.roles])

        return make_embed(
            title="Roles Mapped to Job Tag",
            description=(
                f"ForumTag `{self.name}` is liked to the following roles:\n"
                f"- {roles}"
            ),
            timestamp=False
        )

######################################################################
    def remove_role(self, role: Role) -> None:

        for i, r in enumerate(self.roles):
            if r.id == role.id:
                self.roles.pop(i)

        self.update()

######################################################################
    def update(self, *, role: Optional[Role] = None) -> None:

        if role is not None:
            self.roles.append(role)

        role_ids = [r.id for r in self.roles]

        c = db.connection.cursor()
        c.execute(
            "UPDATE job_tags SET role_ids = %s WHERE channel_id = %s",
            (role_ids, self.channel.id)
        )

        db.connection.commit()
        c.close()

        return

######################################################################
class JobPostings:
    """Represents a collection of data pertaining to job posting
    functions.
    """

    __slots__ = (
        "guild",
        "source_channels",
        "post_channels",
        "tags"
    )

######################################################################
    def __init__(
        self,
        guild: GuildData,
        source_channels: List[ForumChannel],
        post_channels: List[TextChannel],
        tags: List[JobTag]
    ):
        self.guild: GuildData = guild

        self.source_channels: List[ForumChannel] = source_channels
        self.post_channels: List[TextChannel] = post_channels

        self.tags: List[JobTag] = tags

######################################################################
    @classmethod
    async def load(cls: Type[JP], *, bot: KinoKi, guild: GuildData) -> JP:

        source_channels: List[ForumChannel] = []
        post_channels: List[TextChannel] = []

        # Channel type validation is done when the data is stored, so any
        # channels returned during this load will be of the proper type.
        # Unless they're deleted, in which case the ID is ignored and will
        # be overwritten in the database on the next self.update() call.

        connection = db.connection
        c = connection.cursor()
        c.execute(
            "SELECT * FROM job_postings WHERE guild_id = %s",
            (guild.parent.id, )
        )

        data = c.fetchall()[0]

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

        c.execute("SELECT * FROM job_tags WHERE guild_id = %s", (guild.parent.id, ))

        data = c.fetchall()
        c.close()

        tags = []
        roles = []

        for group in data:
            parent_id = group[1]
            tag_name = group[2]
            role_list = group[3]

            parent = None
            for channel in guild.parent.channels:
                if channel.id == parent_id:
                    parent = channel
                    break

            if parent is None:
                continue

            for role_id in [int(r) for r in convert_db_list(role_list)]:
                role = guild.parent.get_role(role_id)
                if role is None:
                    continue
                roles.append(role)

            if not roles:
                continue

            job_tag = JobTag(parent, tag_name, roles)
            tags.append(job_tag)
            roles = []

        return cls(
            guild=guild,
            source_channels=source_channels,
            post_channels=post_channels,
            tags=tags
        )

######################################################################
    async def view_all_mappings(self, interaction: Interaction) -> None:

        pages = []
        for tag in self.tags:
            pages.append(tag.status())

        paginator = Paginator(
            pages=pages,
            loop_pages=True
        )
        await paginator.respond(interaction)

        return

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
    @staticmethod
    def summarize(thread: Thread, message: Message, mention_list: List[str]) -> Embed:

        mention_summary = "\n- ".join(mention_list)

        return make_embed(
            title="New Job Posting!",
            description=(
                f"**New job posting in {thread.parent.mention}!**\n\n"
                
                "**Thread Name:**\n"
                f"{thread.mention}\n\n"
                
                "**Applicable Position(s):**\n"
                f"- {mention_summary}\n\n"

                f"[Click Here to See the Post!]({message.jump_url})"
            ),
            timestamp=True
        )

######################################################################
    def get_tag(self, tag_name: str) -> Optional[JobTag]:

        for tag in self.tags:
            if tag.name == tag_name:
                return tag

        return None

######################################################################
    def tag_parent(self, tag_name: str) -> Optional[ForumChannel]:

        for channel in self.source_channels:
            for tag in channel.available_tags:
                if tag.name == tag_name:
                    return channel

        return None

######################################################################
    def map_tag(self, tag_name: str, role: Role) -> None:

        for tag in self.tags:
            if tag.name == tag_name:
                tag.update(role=role)
                return

        new_tag = JobTag.new(
            guild_id=self.guild.parent.id,
            channel=self.tag_parent(tag_name),
            name=tag_name,
            role=role
        )
        self.tags.append(new_tag)

        return

######################################################################
    def validate_role(self, role: Role) -> Tuple[bool, Optional[List[JobTag]]]:
        """Returns a boolean indicating whether the role is currently
        mapped to any tag.
        """

        tags = []
        for tag in self.tags:
            if role in tag.roles:
                tags.append(tag)

        if tags:
            return True, tags
        else:
            return False, None

######################################################################
    def find_tag_emoji(self, tag: JobTag) -> Optional[PartialEmoji]:

        for channel in self.source_channels:
            if channel.id == tag.channel.id:
                for t in channel.available_tags:
                    if t.name == tag.name:
                        return t.emoji

######################################################################
    def role_status(self, role: Role) -> str:

        _, tags = self.validate_role(role)
        status = f"{role.mention} is linked to the following tags:\n\n"

        for tag in tags:
            status += (
                f"{self.find_tag_emoji(tag)} {tag.name} "
                f"({tag.channel.mention})\n"
            )

        return status

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
