from datetime   import datetime
from discord    import Colour, Embed

from assets.images  import BotImages
######################################################################

__all__ = (
    "ChannelTypeError",
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
    """

    def __init__(self, required_type: str):

        super().__init__(
            title="Invalid Channel Type",
            message="You entered a channel of the incorrect type.",
            solution=f"Channel argument must be of type {required_type}."
        )

######################################################################
