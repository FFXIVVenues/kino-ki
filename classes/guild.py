from discord    import (

)
from typing     import TYPE_CHECKING, Optional, Type, TypeVar

if TYPE_CHECKING:
    from discord.channel    import ForumChannel, TextChannel
    from discord.guild      import Guild
######################################################################

GD = TypeVar("GD", bound="GuildData")

######################################################################
class GuildData:
    """Represents a collection of configurable settings for a guild
    the bot is a member of.
    """

    __slots__ = (
        "guild",
        "job_source_channel",
        "job_post_channel"
    )

######################################################################
    def __init__(self, guild: Guild):

        self.guild: Guild = guild

        self.job_source_channel: Optional[ForumChannel] = None
        self.job_post_channel: Optional[TextChannel] = None

######################################################################
    @classmethod
    def new(cls: Type[GD], guild: Guild) -> GD:

        return cls(
            guild=guild
        )

######################################################################
    def
######################################################################
