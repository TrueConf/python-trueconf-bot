from abc import ABC, abstractmethod
from html import escape
import re


class TextDecoration(ABC):
    @abstractmethod
    def escape(self, value: str) -> str: ...

    @abstractmethod
    def bold(self, value: str) -> str: ...

    @abstractmethod
    def italic(self, value: str) -> str: ...

    @abstractmethod
    def underline(self, value: str) -> str: ...

    @abstractmethod
    def strikethrough(self, value: str) -> str: ...

    @abstractmethod
    def link(self, value: str, url: str) -> str: ...

    @abstractmethod
    def mention(self, value: str, user_id: str) -> str: ...

    @abstractmethod
    def all_mention(self) -> str: ...


class HtmlDecoration(TextDecoration):
    def escape(self, value: str) -> str:
        return escape(value, quote=False)

    def bold(self, value: str) -> str:
        return f"<b>{value}</b>"

    def italic(self, value: str) -> str:
        return f"<i>{value}</i>"

    def underline(self, value: str) -> str:
        return f"<u>{value}</u>"

    def strikethrough(self, value: str) -> str:
        return f"<s>{value}</s>"

    def link(self, value: str, url: str) -> str:
        return f'<a href="{escape(url, quote=True)}">{value}</a>'

    def mention(self, value: str, user_id: str) -> str:
        return self.link(value, f"trueconf:{user_id}")

    def all_mention(self) -> str:
        return "@all"


class MarkdownDecoration(TextDecoration):
    PATTERN = re.compile(r"([_*\[\]()~`>#+\-=|{}.!\\])")

    def escape(self, value: str) -> str:
        return self.PATTERN.sub(r"\\\1", value)

    def bold(self, value: str) -> str:
        return f"**{value}**"

    def italic(self, value: str) -> str:
        return f"*{value}*"

    def underline(self, value: str) -> str:
        return value

    def strikethrough(self, value: str) -> str:
        return f"~~{value}~~"

    def link(self, value: str, url: str) -> str:
        return f"[{value}]({url})"

    def mention(self, value: str, user_id: str) -> str:
        return self.link(value, f"trueconf:{user_id}")

    def all_mention(self) -> str:
        return "@all"


html_decoration = HtmlDecoration()
markdown_decoration = MarkdownDecoration()