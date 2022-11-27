from discord    import ButtonStyle
from discord.ui import Button, InputText, Modal, Select, View, button
from typing     import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from discord    import (
        Interaction,
        Member
    )
######################################################################

__all__ = (
    "KinoView",
    "ConfirmCancelView",
    "CloseMessageView",
)

######################################################################
class TimedOutButton(Button):

    def __init__(self):
        super().__init__(
            style=ButtonStyle.secondary,
            disabled=True,
            emoji="❌"
        )

######################################################################
class KinoView(View):
    """A special subclassed view useful for KinoKi functions."""

    def __init__(self, owner: Member):

        super().__init__()

        self.owner: Member = owner
        self.value: Optional[Any] = None
        self.complete: bool = False

######################################################################
    async def interaction_check(self, interaction: Interaction) -> bool:

        return interaction.user == self.owner

######################################################################
    async def on_timeout(self) -> None:

        self.clear_items()
        self.add_item(TimedOutButton())

        await self._message.edit(view=self)

######################################################################
class ConfirmCancelView(KinoView):
    """A special view giving the option for the user to confirm or
    decline a choice.
    """

    def __init__(self, owner: Member):
        super().__init__(owner=owner)

    @button(
        style=ButtonStyle.success,
        label="Confirm"
    )
    async def confirm(self, btn: Button, interaction: Interaction) -> None:
        self.complete = True
        self.value = True

        await interaction.response.send_message("** **", delete_after=0.1)
        self.stop()

    @button(
        style=ButtonStyle.danger,
        label="Cancel"
    )
    async def cancel(self, btn: Button, interaction: Interaction) -> None:
        self.complete = True
        self.value = False

        await interaction.response.send_message("** **", delete_after=0.1)
        self.stop()

######################################################################
class CloseMessageView(KinoView):
    """A special View that closes the attached message."""

    def __init__(self, owner: Member):
        super().__init__(owner=owner)

    @button(
        style=ButtonStyle.success,
        label="Close"
    )
    async def close(self, btn: Button, interaction: Interaction) -> None:
        self.complete = True
        self.value = True

        await interaction.response.send_message("** **", delete_after=0.1)
        await self.message.delete()
        self.stop()

######################################################################
