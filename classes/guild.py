from __future__ import annotations

from discord    import Guild
from typing     import TYPE_CHECKING, List, Optional, TypeVar

from classes.jobs   import JobPostings

if TYPE_CHECKING:
    from classes.bot    import KinoKi
####################################################################################################

__all__ = ("GuildData", )

####################################################################################################
class GuildData:
    """Represents a collection of various modules of data pertaining
    to a particular guild.

    Attributes:
    -----------
    parent: :class:`discord.Guild`
        The Discord :class:`Guild` object pertaining to the server this data represents.

    jobs_config: :class:`JobsConfiguration`
        The guild-specific settings pertaining to job crossposting commands and functions.
    """

    __slots__ = (
        "parent",
        "job_postings"
    )

####################################################################################################
    def __init__(self, parent: Guild):

        self.parent: Guild = parent
        self.job_postings: Optional[JobPostings] = None

####################################################################################################
    async def load(self, bot: KinoKi):

        self.job_postings = await JobPostings.load(bot=bot, guild=self)

####################################################################################################
####################################################################################################
####################################################################################################

