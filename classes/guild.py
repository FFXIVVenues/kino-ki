from typing     import (
    TYPE_CHECKING,
    Optional,
    TypeVar
)

from classes.job_postings   import JobPostings

if TYPE_CHECKING:
    from discord.guild  import Guild

    from classes.bot    import KinoKi
######################################################################

__all__ = ("GuildData", )

GD = TypeVar("GD", bound="GuildData")

######################################################################
class GuildData:
    """Represents a collection of various modules of data pertaining
    to a particular guild.
    """

    __slots__ = (
        "parent",
        "job_postings"
    )

######################################################################
    def __init__(self, parent: Guild):

        self.parent: Guild = parent

        self.job_postings: Optional[JobPostings] = None

######################################################################
    async def load_classes(self, bot: KinoKi) -> None:

        self.job_postings = await JobPostings.load(bot=bot, guild=self)

######################################################################
