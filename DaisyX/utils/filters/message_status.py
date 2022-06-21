# Copyright (C) 2018 - 2020 MrYacha. All rights reserved. Source code available under the AGPL.
# Copyright (C) 2019 Aiogram
#
# This file is part of DaisyBot.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter

from DaisyX import dp


class NotForwarded(BoundFilter):
    key = "not_forwarded"

    def __init__(self, not_forwarded):
        self.not_forwarded = not_forwarded

    async def check(self, message: types.Message):
        if "forward_from" not in message:
            return True


class NoArgs(BoundFilter):
    key = "no_args"

    def __init__(self, no_args):
        self.no_args = no_args

    async def check(self, message: types.Message):
        if len(message.text.split(" ")) <= 1:
            return True


class HasArgs(BoundFilter):
    key = "has_args"

    def __init__(self, has_args):
        self.has_args = has_args

    async def check(self, message: types.Message):
        if len(message.text.split(" ")) > 1:
            return True


class CmdNotMonospaced(BoundFilter):
    key = "cmd_not_mono"

    def __init__(self, cmd_not_mono):
        self.cmd_not_mono = cmd_not_mono

    async def check(self, message: types.Message):
        return (
            not message.entities
            or message.entities[0]["type"] != "code"
            or message.entities[0]["offset"] >= 1
        )


dp.filters_factory.bind(NotForwarded)
dp.filters_factory.bind(NoArgs)
dp.filters_factory.bind(HasArgs)
dp.filters_factory.bind(CmdNotMonospaced)
