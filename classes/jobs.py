from __future__ import annotations

from dataclasses    import dataclass
from discord.abc    import GuildChannel
from discord        import (
    ChannelType,
    Colour,
    Embed,
    EmbedField,
    ForumChannel,
    ForumTag,
    Interaction,
    Role,
    TextChannel,
)
from discord.ext.pages  import Paginator
from typing         import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union
)

from ui         import *
from utilities  import *

if TYPE_CHECKING:
    from bot    import KinoKi
    from guild  import GuildData
####################################################################################################

__all__ = ("JobPostings", )

####################################################################################################
@dataclass
class JobTag:
    """Represents data involving a Forum Tag / Role Pairing."""

    __slots__ = (
        "channel",
        "parent",
        "roles"
    )

    channel: ForumChannel
    parent: ForumTag
    roles: List[Role]

####################################################################################################
    @classmethod
    def new(
        cls: Type[JobTag],
        *,
        guild_id: int,
        channel: ForumChannel,
        parent: ForumTag,
        role: Role
    ) -> JobTag:

        c = db_connection.cursor()
        c.execute(
            "INSERT INTO job_tags (guild_id, channel_id, tag_id, role_ids) "
            "VALUES (%s, %s, %s, %s)",
            (guild_id, channel.id, parent.id, [role.id])
        )

        db_connection.commit()
        c.close()

        return cls(
            channel=channel,
            parent=parent,
            roles=[role]
        )

####################################################################################################
    def delete(self) -> None:

        c = db_connection.cursor()
        c.execute(
            "DELETE FROM job_tags WHERE channel_id = %s AND tag_id = %s",
            (self.channel.id, self.parent.id)
        )

        db_connection.commit()
        c.close()

        return

####################################################################################################
    def status(self) -> Embed:

        roles = "\n- ".join([role.mention for role in self.roles])

        return make_embed(
            title=f"Roles Mapped to Job Tag: {self.parent.name}",
            description=(
                f"__**Parent Channel:** {self.channel.mention}__\n"
                f"- {roles}"
            ),
            timestamp=False
        )

####################################################################################################
    def remove_role(self, role: Role) -> None:

        for i, r in enumerate(self.roles):
            if r.id == role.id:
                self.roles.pop(i)

        self.update()

####################################################################################################
    def update(self, *, role: Optional[Role] = None) -> None:

        if role is not None:
            self.roles.append(role)

        role_ids = [r.id for r in self.roles]

        c = db_connection.cursor()
        c.execute(
            "UPDATE job_tags SET role_ids = %s WHERE channel_id = %s",
            (role_ids, self.channel.id)
        )

        db_connection.commit()
        c.close()

        return

####################################################################################################
class JobPostings:
    """Represents a collection of data pertaining to job posting functions for a single guild."""

    __slots__ = (
        "guild",
        "source_channels",
        "post_channels",
        "tags",
        "stats"
    )

####################################################################################################
    def __init__(
        self,
        guild: GuildData,
        source_channels: List[ForumChannel],
        post_channels: List[TextChannel],
        tags: List[JobTag],
        stats: Dict[int, int]
    ):

        self.guild: GuildData = guild

        self.source_channels: List[ForumChannel] = source_channels
        self.post_channels: List[TextChannel] = post_channels
        self.tags: List[JobTag] = tags

        self.stats: Dict[int, int] = stats

####################################################################################################
    @classmethod
    async def load(cls: Type[JobPostings], *, bot: KinoKi, guild: GuildData) -> JobPostings:

        source_channels: List[ForumChannel] = []
        post_channels: List[TextChannel] = []

        # Channel type validation is done when the data is stored, so any channels
        # returned during this load will be of the proper type. Unless they're
        # deleted, in which case the ID is ignored and will be overwritten in the
        # database on the next `self.update()` call.

        c = db_connection.cursor()
        c.execute(
            "SELECT sources, destinations FROM job_postings WHERE guild_id = %s",
            (guild.parent.id,)
        )

        data = c.fetchone()

        source_ids = [int(i) for i in convert_database_list(data[0])]
        post_ids = [int(i) for i in convert_database_list(data[1])]

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

        c.execute("SELECT * FROM job_tags WHERE guild_id = %s", (guild.parent.id,))
        data = c.fetchall()

        tags = []
        roles = []

        for group in data:
            channel_id = group[1]
            role_list = group[2]
            tag_id = group[3]

            try:
                parent = await guild.parent.fetch_channel(channel_id)
            except:
                continue

            found = False
            for tag in parent.available_tags:
                if tag.id == tag_id:
                    found = True
                    break

            if not found:
                continue

            for role_id in [int(r) for r in convert_database_list(role_list)]:
                role = await guild.parent._fetch_role(role_id)
                if role is None:
                    continue
                roles.append(role)

            if not roles:
                continue

            job_tag = JobTag(parent, tag, roles)
            tags.append(job_tag)
            roles = []

        c.execute("SELECT * FROM job_stats WHERE guild_id = %s", (guild.parent.id, ))
        stat_records = c.fetchall()
        c.close()

        job_stats: Dict[int, int] = {}
        for stat in stat_records:
            job_stats[stat[0]] = stat[2]

        return cls(
            guild=guild,
            source_channels=source_channels,
            post_channels=post_channels,
            tags=tags,
            stats=job_stats
        )

####################################################################################################
    def all_channels(self) -> List[GuildChannel]:

        return self.post_channels + self.post_channels

####################################################################################################
    def status_all(self) -> Embed:

        fields = [
            EmbedField("__Source Channel(s)__", self.list_sources(), True),
            EmbedField("__Post Channel(s)__", self.list_destinations(), True),
            SeparatorField(6),
            EmbedField("__Posting Stats__", self.posting_stats(), False),
            SeparatorField(6),
        ]

        return make_embed(
            title="Job Crossposting Module",
            fields=fields
        )

####################################################################################################
    def posting_stats(self) -> str:

        ret = ""
        for key, value in self.stats:
            role = self.guild.parent.get_role(key)
            if role is None:
                continue

            ret += f"- {role.mention} -- {value}x Posts\n"

        if not ret:
            ret = "`No Stats Logged Yet`"

        return ret

####################################################################################################
    def source_channel_status(self) -> Embed:

        return make_embed(
            title="Job Cross-posting Source Channel(s)",
            description=(
                "==============================\n"
                f"{self.list_sources()}"
            )
        )

####################################################################################################
    def post_channel_status(self) -> Embed:

        return make_embed(
            title="Job Cross-posting Post Channel(s)",
            description=(
                "==============================\n"
                f"{self.list_destinations()}"
            )
        )

####################################################################################################
    async def add_source_channel(
        self, interaction: Interaction, channel: ForumChannel
    ) -> None:

        if channel not in self.source_channels:
            self.update(source_channel=channel)

        status = self.source_channel_status()
        view = CloseMessageView(interaction.user)

        await interaction.response.send_message(embed=status, view=view)
        await view.wait()

        return

####################################################################################################
    async def add_post_channel(
            self, interaction: Interaction, channel: TextChannel
    ) -> None:

        if channel not in self.post_channels:
            self.update(post_channel=channel)

        status = self.post_channel_status()
        view = CloseMessageView(interaction.user)

        await interaction.response.send_message(embed=status, view=view)
        await view.wait()

        return

####################################################################################################
    async def remove_source(self, interaction: Interaction, channel: ForumChannel) -> None:

        if channel in self.source_channels:
            self.update(remove_channel=channel)

        status = self.source_channel_status()
        view = CloseMessageView(interaction.user)

        await interaction.response.send_message(embed=status, view=view)
        await view.wait()

        return

####################################################################################################
    async def remove_destination(self, interaction: Interaction, channel: TextChannel) -> None:

        if channel in self.post_channels:
            self.update(remove_channel=channel)

        status = self.post_channel_status()
        view = CloseMessageView(interaction.user)

        await interaction.response.send_message(embed=status, view=view)
        await view.wait()

        return

####################################################################################################
    def list_sources(self) -> str:

        if self.source_channels:
            current_sources = "\n- ".join(
                [c.mention for c in self.source_channels]
            )
            return f"- {current_sources}"

        return "`Not Set`"

####################################################################################################
    def list_destinations(self) -> str:

        if self.post_channels:
            post_channels = "\n- ".join(
                [ch.mention for ch in self.post_channels]
            )
            return f"- {post_channels}"

        return "`Not Set`"

####################################################################################################
    def get_tag_parent_channel(self, tag_name: str) -> Optional[ForumChannel]:

        for channel in self.source_channels:
            for tag in channel.available_tags:
                if tag.name.lower() == tag_name.lower():
                    return channel

        return None

####################################################################################################
    def get_parent_tag(self, tag_string: str) -> Optional[ForumTag]:

        for channel in self.source_channels:
            for tag in channel.available_tags:
                if tag.name.lower() == tag_string.lower():
                    return tag

        return None

####################################################################################################
    def check_for_role_mapping(
        self, role: Role, query_tag: Optional[ForumTag] = None
    ) -> Tuple[bool, List[JobTag]]:
        """Returns a boolean indicating whether the provided role is currently mapped
        to the given tag as well as a list of tags the role is currently mapped to.
        """

        found = False
        tags = []

        for tag in self.tags:
            if role in tag.roles:
                found = True
                tags.append(tag)
                # if query_tag is not None and tag.parent.id == query_tag.id:
                #     found = True

        return found, tags

####################################################################################################
    def role_status(self, role: Role) -> str:

        _, tags = self.check_for_role_mapping(role)
        status = f"{role.mention} is linked to the following tags:\n\n"

        for tag in tags:
            tag_emoji = str(tag.parent.emoji) if str(tag.parent.emoji) != "_" else ""
            status += (
                f"{tag_emoji} {tag.parent.name} "
                f"({tag.channel.mention})\n"
            )

        return status

####################################################################################################
    def role_tag_status(self, role: Role) -> Embed:

        _, tags = self.check_for_role_mapping(role)

        description = f"The role {role.mention} is already linked to the following forum tags:\n"
        for t in tags:
            description += f"- {t.parent.name} ({t.channel.mention})\n"

        return make_embed(
            title="Tag/Role Combination Already Mapped",
            description=description,
            timestamp=False
        )

####################################################################################################
    def map_tag(self, tag: ForumTag, role: Role) -> None:

        for t in self.tags:
            if t.parent.id == tag.id:
                t.update(role=role)
                return

        new_tag = JobTag.new(
            guild_id=self.guild.parent.id,
            channel=self.get_tag_parent_channel(tag.name),
            parent=tag,
            role=role
        )
        self.tags.append(new_tag)

        return

####################################################################################################
    async def remove_mapping(
        self,
        interaction: Interaction,
        parent_tag: ForumTag,
        parent_role: Role
    ) -> None:

        # if we're at this point, the tag was already successfully found, therefore,
        # we won't get a null reference error here.
        for tag in self.tags:
            if tag.parent.id == parent_tag.id:
                parent_channel = tag.channel
                break

        confirm = make_embed(
            color=Colour.red(),
            title="Mapping Already Present",
            description=(
                f"The forum tag {parent_tag.name} (in channel {parent_channel.mention})\n"
                f"is already linked to the role {parent_role.mention}.\n\n"

                "**Do you want to __remove__ that mapping?**"
            ),
            timestamp=False
        )
        view = ConfirmCancelView(interaction.user)

        await interaction.response.send_message(embed=confirm, view=view)
        await view.wait()

        if view.value is None or view.value is False:
            return

        tag.remove_role(parent_role)
        self.clean_up_tags()

        success = make_embed(
            color=Colour.green(),
            title="Success!",
            description=(
                f"The forum tag {parent_tag.name} (in channel {parent_channel.mention})\n"
                f"is no longer linked to the role {parent_role.mention}.\n\n"
            ),
            timestamp=True
        )

        await interaction.followup.send(embed=success, delete_after=5)

        return

####################################################################################################
    async def view_all_mappings(self, interaction: Interaction) -> None:

        pages = []
        for tag in self.tags:
            pages.append(tag.status())

        if not pages:
            pages = [
                make_embed(
                    color=Colour.red(),
                    title="No Tags Mapped Yet",
                    description=(
                        "You haven't mapped any tag/role combinations yet.\n\n"
                        
                        "Click here ➡ </jobs map_role:1073421413924483092> ⬅ to do that now!\n\n"
                        
                        "*(Remember, spelling counts~!)*"
                    )
                )
            ]

        paginator = Paginator(
            pages=pages,
            loop_pages=True
        )
        await paginator.respond(interaction)

        return

####################################################################################################
    def role_removed(self, role: Role) -> None:

        for tag in self.tags:
            for i, r in enumerate(tag.roles):
                if r.id == role.id:
                    tag.roles.pop(i)

                    if not tag.roles:
                        tag.delete()

        self.clean_up_tags()

####################################################################################################
    def clean_up_tags(self) -> None:

        for i, tag in enumerate(self.tags):
            print(tag.parent.name)
            print(tag.roles)
            if not tag.roles:
                tag.delete()
                self.tags.pop(i)

####################################################################################################
    def update_stats(self, role: Role) -> None:

        c = db_connection.cursor()

        if role.id not in self.stats.keys():
            self.stats[role.id] = 1
            c.execute(
                "INSERT INTO job_stats (role_id, guild_id, count) VALUES (%s, %s, %s)",
                (role.id, self.guild.parent.id, 1)
            )
        else:
            self.stats[role.id] += 1
            c.execute(
                "UPDATE job_stats SET count = %s WHERE role_id = %s",
                (self.stats[role.id], role.id)
            )

        db_connection.commit()
        c.close()

        return

####################################################################################################
    def yeet_channel(self, channel: ForumChannel) -> None:

        if channel.type is ChannelType.text:
            for i, ch in enumerate(self.post_channels):
                if ch.id == channel.id:
                    self.post_channels.pop(i)
                    break

        elif channel.type is ChannelType.forum:
            for i, ch in enumerate(self.source_channels):
                if ch.id == channel.id:
                    self.source_channels.pop(i)
                    break

            for i, tag in enumerate(self.tags):
                if tag.parent.id == channel.id:
                    tag.delete()
                    self.tags.pop(i)

        self.update()

####################################################################################################
    def update(
        self,
        source_channel: Optional[ForumChannel] = None,
        post_channel: Optional[TextChannel] = None,
        remove_channel: Optional[Union[ForumChannel, TextChannel]] = None
    ) -> None:

        if source_channel is not None:
            self.source_channels.append(source_channel)
        if post_channel is not None:
            self.post_channels.append(post_channel)
        if remove_channel is not None:
            if remove_channel in self.source_channels:
                self.source_channels.remove(remove_channel)
            elif remove_channel in self.post_channels:
                self.post_channels.remove(remove_channel)
            else:
                return

        source_ids = [channel.id for channel in self.source_channels]
        post_ids = [channel.id for channel in self.post_channels]

        c = db_connection.cursor()
        c.execute(
            "UPDATE job_postings SET sources = %s, destinations = %s "
            "WHERE guild_id = %s",
            (source_ids, post_ids, self.guild.parent.id)
        )

        db_connection.commit()
        c.close()

        return

####################################################################################################
