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

from aiogram.types.chat_permissions import ChatPermissions
from aiogram.utils.exceptions import BadRequest, MigrateToChat, Unauthorized

from DaisyX import bot


async def ban_user(chat_id, user_id, until_date=None):
    try:
        await bot.kick_chat_member(chat_id, user_id, until_date=until_date)
    except (BadRequest, MigrateToChat, Unauthorized):
        return False
    return True


async def kick_user(chat_id, user_id):
    await bot.unban_chat_member(chat_id, user_id)
    return True


async def mute_user(chat_id, user_id, until_date=None):
    await bot.restrict_chat_member(
        chat_id,
        user_id,
        permissions=ChatPermissions(can_send_messages=False, until_date=until_date),
        until_date=until_date,
    )
    return True


async def restrict_user(chat_id, user_id, until_date=None):
    await bot.restrict_chat_member(
        chat_id,
        user_id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            until_date=until_date,
        ),
        until_date=until_date,
    )
    return True


async def unmute_user(chat_id, user_id):
    await bot.restrict_chat_member(
        chat_id,
        user_id,
        can_send_messages=True,
        can_send_media_messages=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
    )
    return True


async def unban_user(chat_id, user_id):
    try:
        return await bot.unban_chat_member(chat_id, user_id, only_if_banned=True)
    except (BadRequest, Unauthorized):
        return False
