# This file is part of Daisy (Telegram Bot)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This file is part of Daisy.

from typing import Union


class SanTeXDoc:
    def __init__(self, *args):
        self.items = list(args)

    def __str__(self) -> str:
        return "\n".join([str(items) for items in self.items])

    def __add__(self, other):
        self.items.append(other)
        return self


class StyleFormationCore:
    start: str
    end: str

    def __init__(self, text: str):
        self.text = f"{self.start}{text}{self.end}"

    def __str__(self) -> str:
        return self.text


class Bold(StyleFormationCore):
    start = "<b>"
    end = "</b>"


class Italic(StyleFormationCore):
    start = "<i>"
    end = "</i>"


class Code(StyleFormationCore):
    start = "<code>"
    end = "</code>"


class Pre(StyleFormationCore):
    start = "<pre>"
    end = "</pre>"


class Strikethrough(StyleFormationCore):
    start = "<s>"
    end = "</s>"


class Underline(StyleFormationCore):
    start = "<u>"
    end = "</u>"


class Section:
    def __init__(self, *args, title="", indent=3, bold=True, postfix=":"):
        self.title_text = title
        self.items = list(args)
        self.indent = indent
        self.bold = bold
        self.postfix = postfix

    @property
    def title(self) -> str:
        title = self.title_text
        text = str(Bold(title)) if self.bold else title
        text += self.postfix
        return text

    def __str__(self) -> str:
        text = self.title
        space = " " * self.indent
        for item in self.items:
            text += "\n"

            if type(item) is Section:
                item.indent *= 2
            if type(item) is SList:
                item.indent = self.indent
            else:
                text += space

            text += str(item)

        return text

    def __add__(self, other):
        self.items.append(other)
        return self


class SList:
    def __init__(self, *args, indent=0, prefix="- "):
        self.items = list(args)
        self.prefix = prefix
        self.indent = indent

    def __str__(self) -> str:
        space = " " * self.indent if self.indent else " "
        text = ""
        for idx, item in enumerate(self.items):
            if idx > 0:
                text += "\n"
            text += f"{space}{self.prefix}{item}"

        return text


class KeyValue:
    def __init__(self, title, value, suffix=": "):
        self.title = title
        self.value = value
        self.suffix = suffix

    def __str__(self) -> str:
        return f"{self.title}{self.suffix}{self.value}"


class MultiKeyValue:
    def __init__(self, *items: Union[list, tuple], suffix=": ", separator=", "):
        self.items: list = items
        self.suffix = suffix
        self.separator = separator

    def __str__(self) -> str:
        text = ""
        items_count = len(self.items)
        for idx, item in enumerate(self.items):
            text += f"{item[0]}{self.suffix}{item[1]}"

            if items_count - 1 != idx:
                text += self.separator

        return text
