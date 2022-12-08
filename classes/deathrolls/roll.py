from __future__ import annotations

import random

from discord    import Colour, Embed, EmbedField
from typing     import (
    TYPE_CHECKING,
    List,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union
)

from assets                     import BotEmojis, BotImages
from classes.deathrolls.player  import DeathrollPlayer
from classes.ui.deathrollUI     import *
from utils                      import (
    NULL,
    Player,
    SeparatorField,
    draw_separator,
    make_embed,
    _edit_message_helper
)

if TYPE_CHECKING:
    from discord    import ApplicationContext, Interaction
######################################################################

__all__ = (
    "Deathroll",
    "Roll"
)

DR = TypeVar("DR", bound="Deathroll")

DIE = BotEmojis.DIE
P1 = Player.P1
P2 = Player.P2

######################################################################
class Roll:

    __slots__ = (
        "roll_number",
        "before_roll",
        "after_roll",
        "player"
    )

######################################################################
    def __init__(
        self,
        roll_number: int,
        before_roll: int,
        after_roll: int,
        player: Optional[Player]
    ):

        self.roll_number: int = roll_number
        self.before_roll: int = before_roll
        self.after_roll: int = after_roll
        self.player: Optional[Player] = player

######################################################################
    def __repr__(self) -> str:

        return (
            f"<Roll roll_number={self.roll_number} "
            f"before_roll={self.before_roll} after_roll={self.after_roll}>"
        )

######################################################################
    @property
    def difference(self) -> int:

        return self.before_roll - self.after_roll

######################################################################
    def line_summary(self) -> str:

        return (
            f"*({self.player.name})* **Turn #{self.roll_number}:** "
            f"`{self.before_roll:>3}` {BotEmojis.ARROW_RIGHT} "
            f"{BotEmojis.ARROW_RIGHT} `{self.after_roll:>3}` -- "
            f"*(-{self.difference}!)*"
        )

######################################################################
class Deathroll:

    __slots__ = (
        "id",
        "player_1",
        "player_2",
        "current_roll",
        "rolls",
        "current_player",
        "deathrolling",
        "coin_toss_1",
        "coin_toss_2",
        "_max_value"
    )

######################################################################
    def __init__(
        self,
        roll_id: int,
        player_1: DeathrollPlayer,
        player_2: DeathrollPlayer,
        max_value: int = 999
    ):

        self.id: int = roll_id
        self.player_1: DeathrollPlayer = player_1
        self.player_2: DeathrollPlayer = player_2
        
        self.coin_toss_1: Optional[int] = None
        self.coin_toss_2: Optional[int] = None

        self.current_roll: Optional[int] = None
        self.rolls: List[Roll] = []
        self.current_player: Optional[Player] = None
        self.deathrolling: bool = False
        self._max_value: Optional[int] = max_value

######################################################################
    def __repr__(self) -> str:

        return (
            f"<Deathroll player_1={self.player_1.user.id} "
            f"({self.player_1.name!r}) "
            f"player_2={self.player_2.user.id} "
            f"({self.player_2.name!r}) "
            f"current_roll={self.current_roll} roll_count={len(self.rolls)} "
            f"current_player={self.current_player.name}>"
        )

######################################################################
    def description(self) -> str:

        self.rolls.sort(key=lambda r: r.roll_number)

        if self.current_roll is None:
            summary_string = (
                "═════ **Get Ready!** ═════\n\n"
                
                "Click Below to Roll!"
            )

        elif self.current_roll == 0:
            summary_string = (
                "═════ **Uh Oh!** ═════"
            )

        else:
            summary_string = (
                "═════ **Rolling...** ═════\n\n"
    
                f"{DIE}  __***{self.current_roll}!***__  {DIE}\n"
                # f"*(Out of {self.max_value})*"
            )

        return summary_string

######################################################################
    @property
    def active_player(self) -> DeathrollPlayer:

        if self.current_player is P1:
            return self.player_1
        else:
            return self.player_2

######################################################################
    @property
    def inactive_player(self) -> DeathrollPlayer:

        if self.current_player is P1:
            return self.player_2
        else:
            return self.player_1

######################################################################
    def summary(self) -> Embed:

        self.rolls.sort(key=lambda r: r.roll_number)

        # TODO: Abbreviate list if over a certain number of rolls.
        if self.current_roll is not None:
            results = "═══════ Rolls: ════════\n"

            if len(self.rolls) > 10:
                rolls_group = self.rolls[-10:]
                results += f"{len(self.rolls) - 10} More Rolls...\n"
            else:
                rolls_group = self.rolls

            for roll in rolls_group:
                if roll.player is P1:
                    player = self.player_1
                else:
                    player = self.player_2

                skull = BotEmojis.SKULL_CROSSBONES if roll.after_roll == 0 else ""
                results += (
                    f"{skull} {player.name}: {roll.before_roll} -> "
                    f"{roll.after_roll} (-{roll.difference}) {skull}\n"
                )

        else:
            results = Embed.Empty

        if self.current_roll == 0:
            image = BotImages.YOU_DIED
            icon = BotImages.SKULL_AND_CROSSBONES
            author = f"{self.inactive_player.name} lost!"
            color = Colour.dark_red()
        else:
            image = Embed.Empty
            icon = BotImages.SKULL_DICE
            author = "Deathrolling..."
            color = Colour.embed_background()

        return make_embed(
            color=color,
            author_name=author,
            author_icon=icon,
            description=self.description(),
            image_url=image,
            timestamp=False,
            footer_text=results
        )

######################################################################
    @property
    def max_value(self) -> int:

        return (
            self._max_value if self._max_value is not None
            else self.current_roll
        )

######################################################################
    def coin_toss_result(self) -> Optional[Union[Player, bool]]:

        if self.coin_toss_1 is None or self.coin_toss_2 is None:
            return None

        if self.coin_toss_1 == self.coin_toss_2:
            return False
        elif self.coin_toss_1 > self.coin_toss_2:
            return P1
        else:
            return P2

######################################################################
    def coin_toss_summary(self) -> Embed:

        p1_value = NULL if self.coin_toss_1 is None else f"`{self.coin_toss_1}`"
        p2_value = NULL if self.coin_toss_2 is None else f"`{self.coin_toss_2}`"

        fields = [
            EmbedField(self.player_1.name, f"{DIE} {p1_value}", True),
            EmbedField("|", "|", True),
            EmbedField(self.player_2.name, f"{DIE} {p2_value}", True)
        ]

        if self.coin_toss_result() is not None:
            fields.append(SeparatorField(11))
            if self.coin_toss_result() is False:
                fields.append(
                    EmbedField(f"{DIE} **You tied! Roll again!** {DIE}", "** **", False)
                )
            elif self.coin_toss_result() is P1:
                fields.append(
                    EmbedField(
                        (
                            f"{BotEmojis.ONE} **{self.player_1.name} won "
                            f"the toss! {BotEmojis.ONE}"
                        ),
                        "** **",
                        False
                    )
                )
            else:
                fields.append(
                    EmbedField(
                        (
                            f"{BotEmojis.TWO} {self.player_2.name} won "
                            f"the toss! {BotEmojis.TWO}"
                        ),
                        "** **",
                        False
                    )
                )

        return make_embed(
            author_icon=BotImages.SWASHBUCKLER_COIN,
            author_name="Coin Toss...",
            color=Colour.orange(),
            description=(
                "**Click your respective buttons below** to decide who "
                "goes first!\n"
                "======================================================"
            ),
            timestamp=False,
            fields=fields
        )

######################################################################
    def toss_coin(self, player: Player) -> None:

        toss = random.randint(0, 10)

        if player == P1:
            self.coin_toss_1 = toss
        else:
            self.coin_toss_2 = toss

        return

######################################################################
    def roll(self) -> int:

        number = random.randint(0, self.max_value)

        roll = Roll(
            roll_number=len(self.rolls) + 1,
            before_roll=self.max_value,
            after_roll=number,
            player=self.current_player
        )

        self.rolls.append(roll)
        self.current_roll = number

        # Set to None, so we use the current roll from now on.
        self._max_value = None

        return number

######################################################################
    def change_turn(self) -> DeathrollPlayer:

        if self.current_player is P1:
            self.current_player = P2
            return self.player_2

        else:
            self.current_player = P1
            return self.player_1

######################################################################
    async def play(self, interaction: Interaction) -> None:

        self.deathrolling = True

        # Coin toss first
        coin_toss = self.coin_toss_summary()
        view = CoinTossView(
            owner=self.player_1.user,
            player_2=self.player_2.user,
            deathroll=self
        )

        inter = await interaction.response.send_message(embed=coin_toss, view=view)

        while self.coin_toss_result() is None:
            await view.wait()

            if not view.complete:
                return

            if self.coin_toss_result() is False:
                self.coin_toss_1 = None
                self.coin_toss_2 = None

                view = CoinTossView(
                    owner=self.player_1.user,
                    player_2=self.player_2.user,
                    deathroll=self
                )

                await _edit_message_helper(interaction, view=view)
                continue

            else:
                self.current_player = self.coin_toss_result()

        # Start the deathroll process
        summary = self.summary()
        owner = (
            self.player_1.user if self.current_player is P1
            else self.player_2.user
        )
        view = DeathrollView(owner, self)

        # Do the first response outside the loop, so we only send
        # the message once.
        inter = await interaction.followup.send(embed=summary, view=view)

        while self.deathrolling:
            await view.wait()

            if not view.complete:
                return

            next_roll = self.roll()
            if next_roll == 0:
                self.deathrolling = False

            next_player = self.change_turn()
            view = DeathrollView(next_player.user, self)

            await inter.edit(embed=self.summary(), view=view)

        view = RollOverView(self.player_1, self.player_2)
        await inter.edit(embed=self.summary(), view=view)

        if self.current_player is P1:
            self.player_1.update(won_game=False)
            self.player_2.update(won_game=True)
        else:
            self.player_1.update(won_game=True)
            self.player_2.update(won_game=False)

######################################################################
