from abc        import ABC
from discord    import Bot
from typing     import List

from classes.guild import GuildData
######################################################################
class KinoKi(Bot, ABC):
    """Represents the main bot instance being run.

    Attributes:
    -----------
    k_guilds: :class:`list`
        A list of custom guild objects that hold data pertaining
        to bot features.

    """

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.k_guilds: List[GuildData] = []

######################################################################
