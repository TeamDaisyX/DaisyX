# This file is part of Daisy (Telegram Bot)

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


class OnlyPM(BoundFilter):
    key = "only_pm"

    def __init__(self, only_pm):
        self.only_pm = only_pm

    async def check(self, message: types.Message):
        if message.from_user.id == message.chat.id:
            return True


class OnlyGroups(BoundFilter):
    key = "only_groups"

    def __init__(self, only_groups):
        self.only_groups = only_groups

    async def check(self, message: types.Message):
        if message.from_user.id != message.chat.id:
            return True


dp.filters_factory.bind(OnlyPM)
dp.filters_factory.bind(OnlyGroups)
