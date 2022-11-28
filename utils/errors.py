from datetime   import datetime
from discord    import Colour, Embed

from assets.images  import BotImages
######################################################################

__all__ = (
    "ChannelTypeError",
    "SourceChannelAlreadyExistsError",
    "NoChannelsConfiguredError",
    "ChannelNotFound",

)

######################################################################
class ErrorMessage(Embed):
    """A subclassed Discord embed object, based on code, as an error message.

    Should generally be created via classmethod.
    """

    def __init__(
        self,
        *,
        title: str,
        message: str,
        solution: str,
        description: str = ""
    ):

        super().__init__(
            title=title,
            description=description,
            colour=Colour.red()
        )

        self.add_field(
            name="What Happened?",
            value=message,
            inline=True
        )

        self.add_field(
            name="How to Fix?",
            value=solution,
            inline=True
        )

        self.set_thumbnail(url=BotImages.ERROR_FROG)
        self.timestamp = datetime.now()

######################################################################
class ChannelTypeError(ErrorMessage):
    """An error message for when a channel of an incorrect type
    was provided for a prompt.

    Overview:
    ---------
    Title:
        "Invalid Channel Type"

    Description:
        [None]

    Message:
        "You entered a channel of an incorrect type."

    Solution:
        "Channel argument must be of type ``{required_channel_type}``.

    """

    def __init__(self, required_channel_type: str):

        super().__init__(
            title="Invalid Channel Type",
            message="You entered a channel of an incorrect type.",
            solution=f"Channel argument must be of type {required_channel_type}."
        )

######################################################################
class SourceChannelAlreadyExistsError(ErrorMessage):
    """An error message for when a provided channel is already part
    of the job source channel collection.

    Overview:
    ---------
    Title:
        "Already Listening to that Channel"

    Description:
        "Unable to add {mention} to the list of job posting source
        channels."

    Message:
        "That channel is already a part of the list of job posting
        source channels."

    Solution:
        "Try adding an item that isn't already on the list."

    """

    def __init__(self, mention: str):

        super().__init__(
            title="Already Listening to that Channel",
            description=(
                f"Unable to add {mention} to the list of job posting "
                f"source channels."
            ),
            message=(
                "That channel is already a part of the list of job "
                "posting source channels."
            ),
            solution="Try adding an item that isn't already on the list."
        )

######################################################################
class NoChannelsConfiguredError(ErrorMessage):
    """An error message for when there are no channels listed in a
    particular collection.

    Overview:
    ---------
    Title:
        "No Channels In That Category"

    Description:
        [None]

    Message:
        "There are not channels listed as {channel_type} channels yet."

    Solution:
        "Use `/postings source` to add a channel for crosspost listening."

    """

    def __init__(self, channel_type: str):

        super().__init__(
            title="No Channels In That Category",
            message=(
                f"There are not channels listed as {channel_type} "
                "channels yet."
            ),
            solution=(
                "Use `/postings source` to add a channel for "
                "crosspost listening."
            )
        )

######################################################################
class ChannelNotFound(ErrorMessage):
    """An error message for when a given channel can't be found in a
    particular collection.

    Overview:
    ---------
    Title:
        "Channel Not Found"

    Description:
        [None]

    Message:
        "{channel} could not be found in the list of {channel_type} channels."

    Solution:
        "Make sure you provide a channel that's in the list for that operation."

    """

    def __init__(self, channel: str, channel_type: str):

        super().__init__(
            title="Channel Not Found",
            message=(
                f"{channel} could not be found in the list of "
                f"{channel_type} channels."
            ),
            solution=(
                "Make sure you provide a channel that's in the list "
                "for that operation."
            )
        )

######################################################################
