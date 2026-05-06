
from __future__ import annotations

"""
Utilities for building formatted message text.

The module provides a small tree-based formatting API similar to aiogram's formatting
helpers. Formatting nodes can be composed and rendered either as HTML or Markdown.

Example:
    ```python
    from trueconf.utils.formatting import Bold, Link, Mention, Text

    content = Text(
        Bold("Important"),
        " message for ",
        Mention("John Doe", user_id="john_doe@video.example.com"),
        "\n",
        Link("Open website", url="https://trueconf.com"),
    )

    html = content.as_html()
    markdown = content.as_markdown()
    ```
"""

from abc import ABC, abstractmethod

from .decorations import TextDecoration, html_decoration, markdown_decoration

class TextNode(ABC):
    """
    Base class for all formatting nodes.

    Formatting nodes render themselves using a text decoration strategy, such as
    HTML or Markdown. End users usually do not instantiate this class directly;
    use :class:`Text`, :class:`Bold`, :class:`Italic`, :class:`Link`, and other
    concrete nodes instead.
    """

    @abstractmethod
    def render(self, decoration: TextDecoration) -> str:
        """
        Renders the node using the provided decoration strategy.

        Args:
            decoration (TextDecoration): Formatting strategy used to render the node.

        Returns:
            str: Rendered text.
        """
        ...


class Text(TextNode):
    """
    Container node for plain text and nested formatting nodes.

    Args:
        *body (str | TextNode): Plain strings or formatting nodes to concatenate.

    Example:
        ```python
        content = Text("Hello, ", Bold("world"))
        html = content.as_html()
        ```
    """
    def __init__(self, *body: str | TextNode):
        """
        Initializes a text container.

        Args:
            *body (str | TextNode): Plain strings or formatting nodes.
        """
        self.body = body

    def render(self, decoration: TextDecoration) -> str:
        """
        Renders the text container using the provided decoration strategy.

        Args:
            decoration (TextDecoration): Formatting strategy used for rendering.

        Returns:
            str: Rendered text.
        """
        parts: list[str] = []

        for item in self.body:
            if isinstance(item, TextNode):
                parts.append(item.render(decoration))
            else:
                parts.append(decoration.escape(str(item)))

        return "".join(parts)

    def as_html(self) -> str:
        """
        Renders the text container as HTML.

        Returns:
            str: HTML representation of the formatted text.
        """
        return self.render(html_decoration)

    def as_markdown(self) -> str:
        """
        Renders the text container as Markdown.

        Returns:
            str: Markdown representation of the formatted text.
        """
        return self.render(markdown_decoration)


class Bold(Text):
    """Represents bold text."""
    def render(self, decoration: TextDecoration) -> str:
        """
        Renders the nested content as bold text.

        Args:
            decoration (TextDecoration): Formatting strategy used for rendering.

        Returns:
            str: Rendered bold text.
        """
        return decoration.bold(super().render(decoration))


class Italic(Text):
    """Represents italic text."""
    def render(self, decoration: TextDecoration) -> str:
        """
        Renders the nested content as italic text.

        Args:
            decoration (TextDecoration): Formatting strategy used for rendering.

        Returns:
            str: Rendered italic text.
        """
        return decoration.italic(super().render(decoration))


class Underline(Text):
    """Represents underlined text."""
    def render(self, decoration: TextDecoration) -> str:
        """
        Renders the nested content as underlined text.

        Args:
            decoration (TextDecoration): Formatting strategy used for rendering.

        Returns:
            str: Rendered underlined text.
        """
        return decoration.underline(super().render(decoration))


class Strikethrough(Text):
    """Represents strikethrough text."""
    def render(self, decoration: TextDecoration) -> str:
        """
        Renders the nested content as strikethrough text.

        Args:
            decoration (TextDecoration): Formatting strategy used for rendering.

        Returns:
            str: Rendered strikethrough text.
        """
        return decoration.strikethrough(super().render(decoration))


class Link(Text):
    """
    Represents a hyperlink.

    Args:
        *body (str | TextNode): Link label as plain text or formatting nodes.
        url (str): Link target URL.
    """
    def __init__(self, *body: str | TextNode, url: str):
        """
        Initializes a hyperlink node.

        Args:
            *body (str | TextNode): Link label as plain text or formatting nodes.
            url (str): Link target URL.
        """
        super().__init__(*body)
        self.url = url

    def render(self, decoration: TextDecoration) -> str:
        """
        Renders the nested content as a hyperlink.

        Args:
            decoration (TextDecoration): Formatting strategy used for rendering.

        Returns:
            str: Rendered hyperlink.
        """
        return decoration.link(super().render(decoration), self.url)


class Mention(Text):
    """
    Represents a TrueConf user mention.

    Args:
        *body (str | TextNode): Mention label as plain text or formatting nodes.
        user_id (str): TrueConf user ID, for example ``john_doe@video.example.com``.
    """
    def __init__(self, *body: str | TextNode, user_id: str):
        """
        Initializes a TrueConf mention node.

        Args:
            *body (str | TextNode): Mention label as plain text or formatting nodes.
            user_id (str): TrueConf user ID.
        """
        super().__init__(*body)
        self.user_id = user_id

    def render(self, decoration: TextDecoration) -> str:
        """
        Renders the nested content as a TrueConf user mention.

        Args:
            decoration (TextDecoration): Formatting strategy used for rendering.

        Returns:
            str: Rendered mention.
        """
        return decoration.mention(super().render(decoration), self.user_id)


class AllMention(TextNode):
    """Represents an ``@all`` mention."""
    def render(self, decoration: TextDecoration) -> str:
        """
        Renders an ``@all`` mention.

        Args:
            decoration (TextDecoration): Formatting strategy used for rendering.

        Returns:
            str: Rendered ``@all`` mention.
        """
        return decoration.all_mention()