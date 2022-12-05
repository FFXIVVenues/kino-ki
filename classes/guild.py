from __future__ import annotations

from typing     import (
    TYPE_CHECKING,
    List,
    Optional,
    TypeVar
)

from classes.deathrolls.roll        import Deathroll
from classes.job_postings           import JobPostings

if TYPE_CHECKING:
    from discord.guild  import Guild, User

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
        # "config",
        "job_postings",
        "deathrolls"
    )

######################################################################
    def __init__(self, parent: Guild):

        self.parent: Guild = parent

        # self.config: Optional[GuildConfig] = None
        self.job_postings: Optional[JobPostings] = None
        self.deathrolls: List[Deathroll] = []

######################################################################
    async def load_classes(self, bot: KinoKi) -> None:

        self.job_postings = await JobPostings.load(bot=bot, guild=self)
        # self.config = await GuildConfiguration.load()

######################################################################
    def check_deathroll_duplicates(self, player_1: User, player_2: User) -> bool:

        for deathroll in self.deathrolls:
            if (
                (
                    deathroll.player_1.user == player_1
                    and deathroll.player_2.user == player_2
                ) or
                (
                    deathroll.player_1.user == player_2
                    and deathroll.player_2.user == player_1
                )
            ):
                return True

        return False

######################################################################
