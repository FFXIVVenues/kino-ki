from __future__ import annotations

from discord    import ButtonStyle
from discord.ui import Button, InputText, Modal, Select, View, button
from typing     import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from discord    import Interaction, Member
######################################################################

__all__ = (
    "KinoView",
    "ConfirmCancelView",
    "CloseMessageView",
    "CloseMessageButton"
)

######################################################################
class TimedOutButton(Button):

    def __init__(self):
        super().__init__(
            style=ButtonStyle.secondary,
            label="(Timed Out)",
            disabled=True,
            emoji="❌"
        )

######################################################################
class KinoView(View):
    """A special subclassed view useful for KinoKi functions."""

    def __init__(
        self,
        owner: Member,
        *args,
        close_on_interact: bool = False,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        self.owner: Member = owner
        self.value: Optional[Any] = None
        self.complete: bool = False

        self._interaction: Optional[Interaction] = None
        self._close_on_interact: bool = close_on_interact

######################################################################
    async def interaction_check(self, interaction: Interaction) -> bool:

        if interaction.user == self.owner:
            self._interaction = interaction
            return True

        return False

######################################################################
    async def on_timeout(self) -> None:

        if self.disable_on_timeout:
            self.disable_all_items()
        else:
            self.clear_items()
            self.add_item(TimedOutButton())

        await self.edit_view_helper()

######################################################################
    async def stop(self) -> None:

        super().stop()

        if self._close_on_interact:
            if self._interaction is not None:
                try:
                    await self._interaction.message.delete()
                except:
                    try:
                        await self._interaction.delete_original_response()
                    except:
                        pass

######################################################################
    async def edit_view_helper(self) -> None:
        """Helper function that tries to edit a view's parent message."""

        try:
            await self.message.edit(view=self)
        except:
            try:
                await self._interaction.edit_original_response(view=self)
            except:
                pass

######################################################################
class ConfirmCancelView(KinoView):
    """A special view giving the option for the user to confirm or
    decline a choice.
    """

    def __init__(self, owner: Member, *args, **kwargs):
        super().__init__(owner=owner, *args, **kwargs)

    @button(
        style=ButtonStyle.success,
        label="Confirm"
    )
    async def confirm(self, btn: Button, interaction: Interaction) -> None:
        self.complete = True
        self.value = True

        await interaction.response.send_message("** **", delete_after=0.1)
        await self.stop()

    @button(
        style=ButtonStyle.danger,
        label="Cancel"
    )
    async def cancel(self, btn: Button, interaction: Interaction) -> None:
        self.complete = True
        self.value = False

        await interaction.response.send_message("** **", delete_after=0.1)
        await self.stop()

######################################################################
class CloseMessageView(KinoView):
    """A special View that closes the attached message."""

    def __init__(
        self,
        owner: Member,
        *args,
        close_on_interact: bool = True,
        **kwargs
    ):

        super().__init__(
            owner=owner, close_on_interact=close_on_interact, *args, **kwargs
        )

    @button(
        style=ButtonStyle.success,
        label="Close"
    )
    async def close(self, btn: Button, interaction: Interaction) -> None:
        self.complete = True
        self.value = True

        await interaction.response.send_message("** **", delete_after=0.1)
        await self.stop()

######################################################################
    async def on_timeout(self) -> None:

        self.clear_items()
        await self.edit_view_helper()

######################################################################
class CloseMessageButton(Button):

    def __init__(self):

        super().__init__(
            style=ButtonStyle.success,
            label="Close Message",
            disabled=False,
            row=4
        )

    async def callback(self, interaction: Interaction):
        try:
            await interaction.message.delete()
        except:
            try:
                await interaction.delete_original_response()
            except:
                pass

######################################################################
