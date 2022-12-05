from __future__ import annotations

from datetime       import datetime
from discord        import Colour, Embed, EmbedField
from discord.embeds import EmptyEmbed
from typing         import (
    TYPE_CHECKING,
    Any,
    List,
    Literal,
    Optional,
    Tuple,
    Union
)

from . import colors

if TYPE_CHECKING:
    from discord   import Interaction
######################################################################

__all__ = (
    "make_embed",
    "convert_db_list",
    "SeparatorField",
    "NS",
    "draw_separator",
    "_edit_message_helper",
    "NULL",
    "dummy_reply"
)

######################################################################

NS = "`Not Set`"
NULL = "`---`"

######################################################################
class SeparatorField(EmbedField):

    def __init__(self, length: int):

        super().__init__("=" * (5 * length), "** **", False)

######################################################################
def make_embed(
    *,
    title: str = EmptyEmbed,
    description: str = EmptyEmbed,
    url: str = EmptyEmbed,
    color: Optional[Union[Colour, int]] = colors.random_all(),
    thumbnail_url: str = EmptyEmbed,
    image_url: str = EmptyEmbed,
    footer_text: str = EmptyEmbed,
    footer_icon: str = EmptyEmbed,
    author_name: str = EmptyEmbed,
    author_url: str = EmptyEmbed,
    author_icon: str = EmptyEmbed,
    timestamp: bool = True,
    fields: Optional[List[Union[Tuple[str, Any, bool], EmbedField]]] = None
) -> Embed:
    """Creates and returns a Discord embed with the provided parameters.

    All parameters are optional.

    Parameters:
    -----------
    title: :class:`str`
        The embed's title.

    description: :class:`str`
        The main text body of the embed.

    url: :class:`str`
        The URL for the embed title to link to.

    color: Optional[Union[:class:`Colour`, :class:`int`]]
        The desired accent color. Defaults to :func:`colors.random_all()`

    thumbnail_url: :class:`str`
        The URL for the embed's desired thumbnail image.

    image_url: :class:`str`
        The URL for the embed's desired main image.

    footer_text: :class:`str`
        The text to display at the bottom of the embed.

    footer_icon: :class:`str`
        The icon to display to the left of the footer text.

    author_name: :class:`str`
        The text to display at the top of the embed.

    author_url: :class:`str`
        The URL for the author text to link to.

    author_icon: :class:`str`
        The icon that appears to the left of the author text.

    timestamp: :class:`bool`
        Whether to add the current time to the bottom of the embed.
        Defaults to ``True``.

    fields: Optional[List[Union[Tuple[:class:`str`, Any, :class:`bool`], :class:`EmbedField`]]]
        List of tuples or EmbedFields, each denoting a field to be added
        to the embed. If entry is a tuple, values are as follows:
            0 -> Name | 1 -> Value | 2 -> Inline (bool)

    Returns:
    --------
    :class:`Embed`
        The finished embed object.

    """

    embed = Embed(
        colour=color,
        title=title,
        description=description,
        url=url
    )

    embed.set_thumbnail(url=thumbnail_url)
    embed.set_image(url=image_url)

    if footer_text is not EmptyEmbed:
        embed.set_footer(
            text=footer_text,
            icon_url=footer_icon
        )

    if author_name is not EmptyEmbed:
        embed.set_author(
            name=author_name,
            url=author_url,
            icon_url=author_icon
        )

    if timestamp:
        embed.timestamp = datetime.now()

    if fields is not None:
        if all(isinstance(f, EmbedField) for f in fields):
            embed.fields = fields
        else:
            for f in fields:
                embed.add_field(name=f[0], value=f[1], inline=f[2])

    return embed

######################################################################
def convert_db_list(data: str) -> List[str]:
    """Helper function to convert a list stored as text in the
    database back into a Python list.

    Parameters:
    -----------
        data: :class:`str
            The database text result to be parsed.

    Returns:
    --------
    List[:class:`str`]
        A list with the string versions of all listed items.

    """

    if not data or data == "{}":
        return []

    base_list = [i for i in data.lstrip("{").rstrip("}").split(",")]

    return [i.strip("'").strip('"') for i in base_list]

######################################################################
def draw_separator(text: str, extra: float = 0.0):
    """Helper function to draw a separator line based on the length of
    the provided text.

    Parameters:
    -----------
    text: :class:`str`
        The text to draw a separator for.

    extra: :class:`float`
        The amount of additional separators to include.

    Returns:
    --------
    :class:`str`
        A string of '=' roughly equivalent to the length of the provided
        text.

    """

    text_value: float = 0.0

    for character in text:
        if character in (" ", "i", "j", "l", ","):
            text_value += 0.4
        elif character in ("I", "f", "!"):
            text_value += 0.5
        elif character in ("J", "r", "t", "(", ")", "-", '"', "1"):
            text_value += 0.6
        elif character in ("L", "s", "[", "]"):
            text_value += 0.7
        elif character in ("E", "F", "a", "c", "e", "g", "k", "v", "x", "y", "z", "^", "{", "}", "?"):
            text_value += 0.8
        elif character in ("B", "P", "R", "S", "b", "d", "h", "n", "o", "p", "q", "u", "$", "+", "/", "2", "3", "5", "7"):
            text_value += 0.9
        elif character in ("K", "T", "Z", ">", "<", "4", "6", "8", "9", "0"):
            text_value += 1.0
        elif character in ("C", "U", "V", "X", "Y", "#", "&"):
            text_value += 1.1
        elif character in ("A", "D", "G", "H", "N", "O", "w"):
            text_value += 1.2
        elif character in ("Q"):
            text_value += 1.3
        elif character in ("m", "@"):
            text_value += 1.4
        elif character in ("M", "%"):
            text_value += 1.5
        elif character in ("W"):
            text_value += 1.7
        else:
            pass

    return "=" * int(text_value + extra)

######################################################################
async def _edit_message_helper(interaction: Interaction, *args, **kwargs):
    """A utility function to edit a source message.

    Parameters:
    -----------
    interaction: :class:`Interaction`
        The interaction whose message we are editing.

    *args:
        Any positional arguments being passed to :meth:`Message.edit`.

    **kwargs:
        Any keyword arguments being passed to :meth:`Message.edit`.
    """

    try:
        await interaction.message.edit(*args, **kwargs)
    except:
        try:
            await interaction.edit_original_response(*args, **kwargs)
        except:
            pass

######################################################################
async def dummy_reply(interaction: Interaction) -> None:

    try:
        await interaction.response.send_message("** **", delete_after=0.1)
    except:
        pass

######################################################################
