from discord    import Cog
from typing     import TYPE_CHECKING

from classes.guild  import GuildData

if TYPE_CHECKING:
    from classes.bot    import KinoKi
######################################################################
class Internal(Cog):
    """Handles any necessary internal bot calls."""

    def __init__(self, bot: KinoKi):

        self.bot: KinoKi = bot

######################################################################
    @Cog.listener("on_ready")
    async def load_guilds(self):
        """Loads all special bot config data for each guild."""

        for guild in self.bot.guilds:
            print("====================")
            print(f"Loading: {guild.name} || ID: {guild.id}")

            guild_data = GuildData(parent=guild)
            await guild_data.load_classes(bot=self.bot)

            print("Success!")

            self.bot.k_guilds.append(guild_data)

        print("=================================")
        print("All guilds loaded successfully...")

        return

######################################################################
