from datetime   import datetime
from discord    import Colour, Embed
from typing     import Literal, Optional

from assets     import BotImages
####################################################################################################

__all__ = (
    "ChannelTypeError",
    "SourceTagNotFound",
    "MappingNotFound"
)

####################################################################################################
class ErrorMessage(Embed):
    """A subclassed Discord embed object as an error message."""

    def __init__(
        self,
        *,
        title: str,
        message: str,
        solution: str,
        description: Optional[str] = None
    ):

        super().__init__(
            title=title,
            description=description if description is not None else Embed.Empty,
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

####################################################################################################
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

####################################################################################################
class SourceTagNotFound(ErrorMessage):
    """An error message informing the user that the forum tag specified
    wasn't found in an available source channel.

    Overview:
    ---------
    Title:
        "Tag Not Found"

    Description:
        [None]

    Message:
        "The forum tag you specified wasn't found in any of the designated
        source channels."

    Solution:
        "Ensure you've spelled the tag name properly and that the parent
        forum channel is in the list of available source channels."

    """

    def __init__(self):

        super().__init__(
            title="Tag Not Found",
            message=(
                "The forum tag you specified wasn't found in any of "
                "the designated source channels."
            ),
            solution=(
                "Ensure you've spelled the tag name properly *and* that "
                "the parent forum channel is in the list of available "
                "source channels.\n"
                "</crossposting add_source:1073421413924483092>"
            )
        )

####################################################################################################
class MappingNotFound(ErrorMessage):
    """An error message informing the user that the forum tag / role mapping specified wasn't found.

    Overview:
    ---------
    Title:
        "Mapping Not Found"

    Description:
        [None]

    Message:
        "The forum tag / role map combination you specified hasn't been created yet."

    Solution:
        "Use </ jobs map_role:1073421413924483092> to create a new mapping."

    """

    def __init__(self):

        super().__init__(
            title="Mapping Not Found",
            message="The forum tag/role map combination you specified hasn't been created yet.",
            solution="Use </jobs map_role:1073421413924483092> to create a new mapping."
        )

####################################################################################################
