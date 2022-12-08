from __future__ import annotations

from discord    import ButtonStyle
from discord.ui import Button, button, View
from typing     import TYPE_CHECKING, Literal, Union

from assets     import BotEmojis
from utils      import KinoView, Player, _edit_message_helper, dummy_reply

if TYPE_CHECKING:
    from discord    import Interaction, Member, User

    from classes.deathrolls.roll    import Deathroll
    from classes.deathrolls.player  import DeathrollPlayer
######################################################################

P1 = Player.P1
P2 = Player.P2

######################################################################

__all__ = (
    "DeathrollView",
    "ConfirmDeclineView",
    "CoinTossView",
    "RollOverView"
)

######################################################################
class DeathrollButton(Button):

    def __init__(self, name: str):

        super().__init__(
            style=ButtonStyle.primary,
            label=f"{name}'s Roll",
            emoji=BotEmojis.DIE,
            disabled=False,
            row=0
        )

    async def callback(self, interaction: Interaction):
        self.view.complete = True

        await dummy_reply(interaction)
        await self.view.stop()  # type: ignore

######################################################################
class DeathrollView(KinoView):

    def __init__(self, owner: Union[Member, User], deathroll: Deathroll):

        super().__init__(owner, close_on_interact=False, timeout=60.0)

        self.roll: Deathroll = deathroll
        self.add_item(DeathrollButton(self.current_name))

######################################################################
    async def interaction_check(self, interaction: Interaction) -> bool:

        if (
            self.roll.current_player is P1
            and interaction.user.id == self.roll.player_1.user.id
        ) or (
            self.roll.current_player is P2
            and interaction.user.id == self.roll.player_2.user.id
        ):
            return True

        return False

######################################################################
    @property
    def current_name(self) -> str:

        if self.roll.current_player is P1:
            return self.roll.player_1.name
        else:
            return self.roll.player_2.name

######################################################################
class ConfirmDeclineView(KinoView):

    def __init__(self, owner: Union[Member, User]):
        super().__init__(owner, close_on_interact=True, timeout=300.0)

    @button(
        style=ButtonStyle.success,
        label="Confirm",
        disabled=False,
        row=0
    )
    async def confirm(self, btn: Button, interaction: Interaction):
        self.complete = True
        self.value = True

        await dummy_reply(interaction)
        await self.stop()

    @button(
        style=ButtonStyle.danger,
        label="Decline",
        disabled=False,
        row=0
    )
    async def decline(self, btn: Button, interaction: Interaction):
        self.complete = True
        self.value = False

        await dummy_reply(interaction)
        await self.stop()

######################################################################
class CoinTossButton(Button):

    def __init__(self, player_name: str, player: Literal[1, 2]):

        super().__init__(
            style=ButtonStyle.primary,
            label=player_name,
            disabled=False,
            row=0,
            custom_id=f"player{player}"
        )

        self.player: int = player

    async def callback(self, interaction: Interaction):
        if self.player == 1:
            self.view.children[0].disabled = True  # type: ignore
            self.view.roll.toss_coin(P1)
        else:
            self.view.children[1].disabled = True  # type: ignore
            self.view.roll.toss_coin(P2)

        embed = self.view.roll.coin_toss_summary()
        await _edit_message_helper(interaction, embed=embed, view=self.view)

        if all([item.disabled for item in self.view.children]):  # type: ignore
            self.view.complete = True
            await self.view.stop()  # type: ignore

        await dummy_reply(interaction)

######################################################################
class CoinTossView(KinoView):

    def __init__(
        self,
        owner: Union[Member, User],
        player_2: Union[Member, User],
        deathroll: Deathroll
    ):
        super().__init__(owner, close_on_interact=False)

        self.owner: Union[Member, User] = owner
        self.player_2: Union[Member, User] = player_2
        self.roll: Deathroll = deathroll

        p1_name = deathroll.player_1.name
        p2_name = deathroll.player_2.name

        self.add_item(CoinTossButton(p1_name, 1))
        self.add_item(CoinTossButton(p2_name, 2))

######################################################################
    async def interaction_check(self, interaction: Interaction) -> bool:

        if interaction.custom_id == "player1":
            if interaction.user.id == self.owner.id:
                return True

        if interaction.custom_id == "player2":
            if interaction.user.id == self.player_2.id:
                return True

        return False

######################################################################
class RollOverView(KinoView):

    def __init__(
        self,
        owner: DeathrollPlayer,
        player_2: DeathrollPlayer,
    ):
        super().__init__(owner.user, timeout=60.0)

        self.owner: DeathrollPlayer = owner
        self.player_2: DeathrollPlayer = player_2

        self.p1_sent: bool = False
        self.p2_sent: bool = False

    @button(
        style=ButtonStyle.secondary,
        disabled=True,
        emoji=BotEmojis.CROSS,
        row=0
    )
    async def nothing(self, btn: Button, interaction: Interaction):

        pass

    @button(
        style=ButtonStyle.primary,
        label="DM Stats",
        disabled=False,
        emoji=BotEmojis.ENVELOPE,
        row=0
    )
    async def stats(self, btn: Button, interaction: Interaction):

        if interaction.user == self.owner.user:
            stats = self.owner.stats()
            self.p1_sent = True
        else:
            stats = self.player_2.stats()
            self.p2_sent = True

        await interaction.user.send(embed=stats)

        if self.p1_sent and self.p2_sent:
            await self.stop()

######################################################################
    async def interaction_check(self, interaction: Interaction) -> bool:

        if interaction.user.id == self.owner.user.id:
            if not self.p1_sent:
                return True

        elif interaction.user.id == self.player_2.user.id:
            if not self.p2_sent:
                return True

        return False

######################################################################

######################################################################
