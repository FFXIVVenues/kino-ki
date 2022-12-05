"""Main project file. Initializes client connection and status loop."""

import os

from discord        import Game, Intents
from discord.ext    import tasks
from dotenv         import load_dotenv
from itertools      import cycle

from classes.bot    import KinoKi
######################################################################
# Secret things

load_dotenv()

######################################################################

bot = KinoKi(
    debug_guilds=[303742308874977280, 221377146638041108],
    intents=Intents.all()
)

######################################################################
# Load status list into memory for usage in change_status()`

status_list = []
with open("./resources/statuses.txt", "r") as filehandle:
    for line in filehandle:
        status_list.append(line.strip())
statuses = cycle(status_list)

######################################################################
@bot.event
async def on_ready():
    """Confirms readiness to logs, and begins status cycling."""

    # Confirm bot load.
    print("Kino Ki Online!")

    # Start the status change loop.
    await change_status.start()

######################################################################
@tasks.loop(hours=2)
async def change_status():
    """Cycles through the list of loaded statuses and sets
    the bot's current activity to 'Playing: [activity]'."""

    await bot.change_presence(activity=Game(next(statuses)))

######################################################################
# Load modules - This part is magic.

for filename in os.listdir("./cogs"):
    if filename.endswith(".py") and filename != "__init__.py":
        bot.load_extension(f"cogs.{filename[:-3]}")

######################################################################
# Ready go!

bot.run(os.getenv("DISCORD_TOKEN"))

######################################################################
