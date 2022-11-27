from discord    import ApplicationContext
from typing     import (
    TYPE_CHECKING,
    List,
    Optional,
    Type,
    TypeVar
)

from utils import (
    CloseMessageView,
    ConfirmCancelView,
    KinoView,
    convert_db_list,
    database as db,
    make_embed,
)

if TYPE_CHECKING:
    from discord    import (
        Embed,
        ForumChannel,
        TextChannel
    )

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

        # Channel type validation is done when the data is stored, so any
        # channels returned during this load will be of the proper type.

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
    def source_channel_status(self) -> Embed:

        joined = "- " + "\n- ".join(ch.mention for ch in self.source_channels)
        description = (
            "=============================="
            f"{joined}"
        )

        return make_embed(
            title="Job Posting Source Channel(s)",
            description=description
        )

######################################################################
    async def add_source_channel(
        self, ctx: ApplicationContext, channel: ForumChannel
    ) -> None:

        current_sources = "\n- ".join([c.mention for c in self.source_channels])
        current_sources = f"- {current_sources}"

        if not self.source_channels:
            self.source_channels = [channel]
        else:
            confirm = make_embed(
                title="Confirm Job Source Channel Add",
                description=(
                    "There are currently one or more channels already "
                    "configured as the source(s) for job cross-postings. "
                    "\n\n"
                    "Current Job Posting Source Channels:\n"
                    f"{current_sources}\n\n"
                    
                    "=============================="
                    f"Please confirm you wish you add "
                    f"{channel.mention} to this list."
                )
            )

            view = ConfirmCancelView(owner=ctx.user)

            await ctx.respond(embed=confirm, view=view)
            await view.wait()

            if not view.complete:
                return

            self.source_channels.append(channel)

        status = self.source_channel_status()
        view = CloseMessageView(owner=ctx.user)

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
