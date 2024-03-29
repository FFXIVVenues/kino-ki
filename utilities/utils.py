from datetime       import datetime
from discord        import (
    Colour,
    Embed,
    EmbedField,
)
from discord.embeds import EmptyEmbed
from typing         import (
    Any,
    List,
    Optional,
    Tuple,
    Union
)

from .colors    import random_all
####################################################################################################

__all__ = (
    "convert_database_list",
    "make_embed",
    "SeparatorField"
)

####################################################################################################
class SeparatorField(EmbedField):

    def __init__(self, length: int):
        super().__init__("=" * (5 * length), "** **", False)

####################################################################################################
def convert_database_list(data: str) -> List[str]:
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

    base_list = [i for i in data[1:-1].split(",")]

    return [i.strip("'").strip('"') for i in base_list]

####################################################################################################
def make_embed(
    *,
    title: str = EmptyEmbed,
    description: str = EmptyEmbed,
    url: str = EmptyEmbed,
    color: Optional[Union[Colour, int]] = random_all(),
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
                if isinstance(f, EmbedField):
                    embed.fields.append(f)
                else:
                    embed.add_field(name=f[0], value=f[1], inline=f[2])

    return embed

####################################################################################################

####################################################################################################

####################################################################################################

####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
