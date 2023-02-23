from __future__ import annotations

from abc        import ABC
from discord    import Bot
from typing     import TYPE_CHECKING, List

if TYPE_CHECKING:
    from guild  import GuildData
####################################################################################################

__all__ = ("KinoKi", )

####################################################################################################
class KinoKi(Bot, ABC):
    """Represents the main bot instance being run.

        Attributes:
        -----------
        k_guilds: List[:class:`GuildData`]
            A list of custom guild objects that hold data pertaining
            to bot features.

    """

    __slots__ = ("k_guilds", )

####################################################################################################

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.k_guilds: List[GuildData] = []

####################################################################################################
