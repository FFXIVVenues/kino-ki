import random

from discord    import (
    ApplicationContext,
    Cog,
    Interaction,
    Member,
    Option,
    SlashCommandOptionType,
    User,
    slash_command
)
from typing     import TYPE_CHECKING

from assets                     import BotEmojis, BotImages
from classes.deathrolls.roll    import Deathroll
from classes.deathrolls.player  import DeathrollPlayer
from classes.ui.deathrollUI     import *
from utils                      import (
    CloseMessageView,
    make_embed
)
from utils.errors               import *

if TYPE_CHECKING:
    from classes.bot    import KinoKi
    from classes.guild  import GuildData
######################################################################
class Deathrolls(Cog):

    def __init__(self, bot: "KinoKi"):

        self.bot: "KinoKi" = bot

######################################################################
    @slash_command(
        name="random",
        description="Roll a random number!"
    )
    async def random_roll(
        self,
        ctx: ApplicationContext,
        number: Option(
            SlashCommandOptionType.integer,
            name="range",
            description="The upper limit cap for this random roll.",
            min_value=0,
            max_value=999,
            default=999
        )
    ) -> None:

        roll = random.randint(0, number + 1)

        result = make_embed(
            description=f"***{roll}***",
            footer_text=ctx.user.display_name,
            timestamp=True
        )

        await ctx.respond(embed=result)

        return

######################################################################
    @slash_command(
        name="deathroll",
        description="Challenge another server member to a deathroll match!"
    )
    async def deathroll(
        self,
        ctx: ApplicationContext,
        orig_player_2: Option(
            SlashCommandOptionType.user,
            name="opponent",
            description="The person you wish to challenge to a deathroll.",
            required=True
        ),
        max_value: Option(
            SlashCommandOptionType.integer,
            name="max_value",
            description="The upper limit cap for this deathroll.",
            min_value=1,
            max_value=999,
            default=999
        )
    ) -> None:

        # if ctx.user == player_2:
        #     error =

        guild_data = self.get_guild(ctx.guild_id)

        active_game = guild_data.check_deathroll_duplicates(ctx.user, orig_player_2)
        if active_game:
            error = DeathrollInProgress(orig_player_2.mention)
            await ctx.respond(embed=error, ephemeral=True)
            return

        # confirm = await confirm_start(ctx.interaction, ctx.user, orig_player_2)
        # if confirm is False:
        #     return

        member_1 = ctx.guild.get_member(ctx.user.id)
        member_2 = ctx.guild.get_member(orig_player_2.id)

        player_1 = self.get_deathroll_player(ctx.user)
        player_2 = self.get_deathroll_player(orig_player_2)

        # Reassigning so we have access to the guild display name.
        player_1.user = member_1
        player_2.user = member_2

        guild_data.deathrolls.sort(key=lambda r: r.roll_id, reverse=True)
        roll_id = guild_data.deathrolls[0].id + 1 if guild_data.deathrolls else 1

        deathroll = Deathroll(
            roll_id=roll_id,
            player_1=player_1,
            player_2=player_2,
            max_value=max_value
        )
        guild_data.deathrolls.append(deathroll)

        await deathroll.play(ctx.interaction)

        # Set the user back to a User in case their profile is called
        # from a different guild.
        player_1.user = ctx.user
        player_2.user = orig_player_2

        for i, roll in enumerate(guild_data.deathrolls):
            if roll.id == roll_id:
                guild_data.deathrolls.pop(i)
                break

        return

######################################################################
    def get_guild(self, guild_id: int) -> "GuildData":

        for guild in self.bot.k_guilds:
            if guild.parent.id == guild_id:
                return guild

######################################################################
    def get_deathroll_player(self, user: Member) -> DeathrollPlayer:

        for player in self.bot.deathroll_players:
            if player.user == user:
                return player

        # If we're here, that means the player isn't in the system yet.
        return DeathrollPlayer.new(user)

######################################################################
def setup(bot: "KinoKi") -> None:
    """Setup function required by commands.Cog superclass
    to integrate module into the bot. Basically magic.

    Args:
        bot: The Bot... duh. Yes, I'm putting this every time.

    """

    bot.add_cog(Deathrolls(bot))

######################################################################
async def confirm_start(
    interaction: Interaction, player_1: Member, player_2: Member
) -> bool:

    prompt = make_embed(
        title="You've Been Challenged...",
        description=(
            f"{player_2.mention}, you've been challenged to a\n"
            f"deathroll by {player_1.mention}.\n\n"
            
            "**DO YOU ACCEPT?**\n"
            "*(Select your response below)*\n"
            "========================="
        ),
        footer_text="This prompt expires in 5 minutes.",
        timestamp=True
    )

    # Player 2 is the view owner here since they're the one replying.
    view = ConfirmDeclineView(player_2)

    await interaction.response.send_message(embed=prompt, view=view)
    await view.wait()

    if not view.complete:
        return False

    if view.value is True:
        return True

    confirm = make_embed(
        title="Challenge Declined",
        description=(
            f"{player_2.mention} has declined the challenge. Sorry!"
        ),
        timestamp=False
    )
    view = CloseMessageView(player_1)

    await interaction.followup.send(embed=confirm, view=view)
    await view.wait()

    return False

######################################################################
