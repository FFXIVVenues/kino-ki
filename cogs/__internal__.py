from __future__ import annotations

from discord    import Cog
from typing     import TYPE_CHECKING

from classes.guild  import GuildData
from utilities      import assert_database_entries

if TYPE_CHECKING:
    from classes.bot    import KinoKi
####################################################################################################
class Internal(Cog):

    def __init__(self, bot: KinoKi):

        self.bot: KinoKi = bot

####################################################################################################
    @Cog.listener("on_ready")
    async def load_guilds(self):
        """Loads all special bot config data for each guild."""

        for guild in self.bot.guilds:
            print("========================================")
            print(f"Loading: {guild.name} || ID: {guild.id}")

            assert_database_entries(guild.id)

            guild_data = GuildData(parent=guild)
            await guild_data.load(bot=self.bot)

            print("Success!")

            self.bot.k_guilds.append(guild_data)

####################################################################################################
def setup(bot: KinoKi) -> None:
    """Setup function required by commands.Cog superclass
    to integrate module into the bot. Basically magic.

    Args:
        bot: The Bot... duh. Yes, I'm putting this every time.

    """

    bot.add_cog(Internal(bot))

####################################################################################################