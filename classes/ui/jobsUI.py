from __future__ import annotations

from discord    import (
    ButtonStyle,
    ComponentType,
    ChannelType,
    SelectOption
)
from discord.ui import Button, Select
from typing     import TYPE_CHECKING, List, Union

from utils      import CloseMessageButton, KinoView

if TYPE_CHECKING:
    from discord        import (
        ForumChannel,
        Interaction,
        Member,
        TextChannel
    )
    from discord.abc    import GuildChannel

    from classes.job_postings   import JobPostings
######################################################################
__all__ = (
    "CrosspostStatusView",
    "ChannelSelectView"
)
######################################################################
class AddSourceChannelButton(Button):

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
class RemoveSourceChannelButton(Button):

    def __init__(self, disabled: bool):
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Source Channel",
            disabled=disabled,
            row=0
        )

    async def callback(self, interaction: Interaction):
        await self.view.postings.menu_remove_source_channel(interaction)

######################################################################
class AddPostChannelButton(Button):

    def __init__(self):
        super().__init__(
            style=ButtonStyle.primary,
            label="Add Post Channel",
            disabled=False,
            row=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.postings.menu_add_post_channel(interaction)

######################################################################
class RemovePostChannelButton(Button):

    def __init__(self, disabled: bool):
        super().__init__(
            style=ButtonStyle.danger,
            label="Remove Post Channel",
            disabled=disabled,
            row=1
        )

    async def callback(self, interaction: Interaction):
        await self.view.postings.menu_remove_post_channel(interaction)

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

        source_disabled = False if self.postings.source_channels else True
        post_disabled = False if self.postings.post_channels else True

        button_list = [
            AddSourceChannelButton(),
            RemoveSourceChannelButton(source_disabled),
            AddPostChannelButton(),
            RemovePostChannelButton(post_disabled),
            CloseMessageButton()
        ]

        for item in button_list:
            self.add_item(item)

######################################################################
class ChannelSelect(Select):

    def __init__(self, channel_list: List[GuildChannel]):
        super().__init__(
            placeholder="Select a channel...",
            options=[
                SelectOption(label=channel.name, value=str(channel.id))
                for channel in channel_list
            ]
        )

    async def callback(self, interaction: Interaction):
        self.view.complete = True

        for channel in interaction.guild.channels:
            if channel.id == int(self.values[0]):
                self.view.value = channel
                break

        await interaction.response.send_message("** **", delete_after=0.1)
        await self.view.stop()  # type: ignore

######################################################################
class ChannelSelectView(KinoView):

    def __init__(self, owner: Member, channel_list: List[GuildChannel]):

        super().__init__(owner, close_on_interact=True)

        if len(channel_list) <= 25:
            self.add_item(ChannelSelect(channel_list))
            self.add_item(CloseMessageButton())

        else:
            all_channels = []
            sublist = []
            count = 0

            for channel in channel_list:
                sublist.append(channel)
                count += 1

                if count == 25:
                    all_channels.append(sublist)
                    sublist = []
                    count = 0

            if count:
                all_channels.append(sublist)

            for channel_group in all_channels:
                self.add_item(ChannelSelect(channel_group))

            if len(all_channels) <= 4:
                self.add_item(CloseMessageButton())

######################################################################
