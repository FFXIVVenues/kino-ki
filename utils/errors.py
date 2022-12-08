from datetime   import datetime
from discord    import Colour, Embed
from typing     import Literal, Optional

from assets.images  import BotImages
######################################################################

__all__ = (
    "ChannelTypeError",
    "ChannelAlreadyExistsError",
    "NoChannelsConfiguredError",
    "ChannelNotFound",
    "DeathrollInProgress",
    "SourceTagNotFound",
    "TagNotMapped",
    "RoleNotMapped",

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
class ChannelAlreadyExistsError(ErrorMessage):
    """An error message for when a provided channel is already part
    of the job source channel collection.

    Overview:
    ---------
    Title:
        "Already Listening to that Channel"

    Description:
        "Unable to add {mention} to the list of job posting
        {channel_type} channels."

    Message:
        "That channel is already a part of the list of job posting
        source channels."

    Solution:
        "Try adding an item that isn't already on the list."

    """

    def __init__(
        self, mention: str, channel_type: Literal["Source", "Destination"]
    ):

        super().__init__(
            title="Already Listening to that Channel",
            description=(
                f"Unable to add {mention} to the list of job posting "
                f"{channel_type} channels."
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
class DeathrollInProgress(ErrorMessage):
    """An error message informing the user that a deathroll with the
    given opponent is already in progress.

    Overview:
    ---------
    Title:
        "Deathroll Already in Progress"

    Description:
        [None]

    Message:
        "You already have an active deathroll open against {player_2}."

    Solution:
        "Finish the current deathroll before starting another."

    """

    def __init__(self, player_2: str):

        super().__init__(
            title="Deathroll Already in Progress",
            message=(
                "You already have an active deathroll open against "
                f"{player_2}."
            ),
            solution="Finish the current deathroll before starting another."
        )

######################################################################
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
        "The forum tag you specified wasn't found in any of the available
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
                "the available source channels."
            ),
            solution=(
                "Ensure you've spelled the tag name properly *and* that "
                "the parent forum channel is in the list of available "
                "source channels.\n"
                "(`/crossposting add_source`)>"
            )
        )

######################################################################
class TagNotMapped(ErrorMessage):
    """An error message informing the user that the specified forum tag
    hasn't been assigned a mapping.

    Overview:
    ---------
    Title:
        "Tag Not Mapped"

    Description:
        [None]

    Message:
        "The forum tag you specified hasn't been mapped to a role(s) yet."

    Solution:
        "Ensure you've spelled the tag name properly."

    """

    def __init__(self):

        super().__init__(
            title="Tag Not Mapped",
            message=(
                "The forum tag you specified hasn't been mapped to a "
                "role(s) yet."
            ),
            solution="Ensure you've spelled the tag name properly."
        )

######################################################################
class RoleNotMapped(ErrorMessage):
    """An error message informing the user that the specified guild role
    hasn't been assigned a tag mapping.

    Overview:
    ---------
    Title:
        "Role Not Mapped"

    Description:
        [None]

    Message:
        - "The role you provided hasn't been mapped to a ForumTag."
        - "The role you provided hasn't been mapped to ForumTag: {tag_name}."

    Solution:
        "To add a mapping, use `/crosspost map_role`."

    """

    def __init__(self, tag_name: Optional[str] = None):

        if tag_name is not None:
            message = (
                "The role you provided hasn't been mapped to ForumTag: "
                f"{tag_name}."
            )
        else:
            message = "The role you provided hasn't been mapped to a ForumTag."

        super().__init__(
            title="Role Not Mapped",
            message=message,
            solution="To add a mapping, use `/crosspost map_role`."
        )

######################################################################
