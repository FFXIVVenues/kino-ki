from __future__ import annotations

from discord    import (
    ButtonStyle,
    ComponentType,
    ChannelType,
    SelectOption
)
from discord.ui import Button, Select
from typing     import TYPE_CHECKING, List

from utils      import CloseMessageButton, KinoView

if TYPE_CHECKING:
    from discord    import (
        ForumChannel,
        Interaction,
        Member,
        TextChannel
    )

    from classes.job_postings   import JobPostings
######################################################################
__all__ = (
    "CrosspostStatusView",
    "ChannelSelectView",
    "StringChannelSelectView"
)
######################################################################
class SourceChannelsButton(Button):

    def __init__(self):
        super().__init__(
            style=ButtonStyle.primary,
            label="Add Source Channel",
            disabled=False,
            row=0
        )

    async def callback(self, interaction: Interaction):
        await self.view.postings.menu_add_source_channel(interaction)

######################################################################

######################################################################
class CrosspostStatusView(KinoView):

    def __init__(
        self,
        owner: Member,
        postings: JobPostings,
        *args,
        **kwargs
    ):

        super().__init__(
            owner, *args, close_on_interact=False, **kwargs
        )

        self.postings: JobPostings = postings

######################################################################
class ChannelSelect(Select):

    def __init__(self, types: List[ChannelType]):
        super().__init__(
            select_type=ComponentType.channel_select,
            placeholder="Select a channel...",
            channel_types=types,
        )

    async def callback(self, interaction: Interaction):
        self.view.value = self.values[0]
        self.view.complete = True

        await interaction.response.send_message("** **", delete_after=0.1)
        await self.view.stop()  # type: ignore

######################################################################
class ChannelSelectView(KinoView):

    def __init__(self, owner: Member, channel_types: List[ChannelType]):

        super().__init__(owner, close_on_interact=True)
        self.add_item(ChannelSelect(channel_types))

######################################################################
class StringChannelSelect(Select):

    def __init__(self, channel_list: List[ForumChannel]):

        super().__init__(
            placeholder="Select a channel...",
            options=[
                SelectOption(label=channel.name, value=str(channel.id))
                for channel in channel_list
            ]
        )

    async def callback(self, interaction: Interaction):
        self.view.complete = True
        self.view.value = int(self.values[0])

        await interaction.response.send_message("** **", delete_after=0.1)
        await self.view.stop()  # type: ignore

######################################################################
class StringChannelSelectView(KinoView):

    def __init__(self, owner: Member, channel_list: List[ForumChannel]):

        super().__init__(owner)
        self.add_item(StringChannelSelect(channel_list))
        self.add_item(CloseMessageButton())

######################################################################
