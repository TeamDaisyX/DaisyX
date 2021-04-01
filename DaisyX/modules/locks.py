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

import itertools

from aiogram.types.chat_permissions import ChatPermissions

from DaisyX import bot
from DaisyX.decorator import register

from .utils.connections import chat_connection
from .utils.language import get_strings_dec


@register(cmds=["locks", "locktypes"], user_admin=True)
@chat_connection(only_groups=True)
@get_strings_dec("locks")
async def lock_types(message, chat, strings):
    chat_id = chat["chat_id"]
    chat_title = chat["chat_title"]
    text = strings["locks_header"].format(chat_title=chat_title)

    async for lock, status in lock_parser(chat_id):
        text += f"- {lock} = {status} \n"
    await message.reply(text)


@register(cmds="lock", user_can_restrict_members=True, bot_can_restrict_members=True)
@chat_connection(only_groups=True)
@get_strings_dec("locks")
async def lock_cmd(message, chat, strings):
    chat_id = chat["chat_id"]
    chat_title = chat["chat_title"]

    if (args := message.get_args().split(" ", 1)) == [""]:
        await message.reply(strings["no_lock_args"])
        return

    async for lock, status in lock_parser(chat_id, rev=True):
        if args[0] == lock[0]:
            if status is True:
                await message.reply(strings["already_locked"])
                continue

            to_lock = {lock[1]: False}
            new_perm = ChatPermissions(**to_lock)
            await bot.set_chat_permissions(chat_id, new_perm)
            await message.reply(
                strings["locked_successfully"].format(lock=lock[0], chat=chat_title)
            )


@register(cmds="unlock", user_can_restrict_members=True, bot_can_restrict_members=True)
@chat_connection(only_groups=True)
@get_strings_dec("locks")
async def unlock_cmd(message, chat, strings):
    chat_id = chat["chat_id"]
    chat_title = chat["chat_title"]

    if (args := message.get_args().split(" ", 1)) == [""]:
        await message.reply(strings["no_unlock_args"])
        return

    async for lock, status in lock_parser(chat_id, rev=True):
        if args[0] == lock[0]:
            if status is False:
                await message.reply(strings["not_locked"])
                continue

            to_unlock = {lock[1]: True}
            new_perm = ChatPermissions(**to_unlock)
            await bot.set_chat_permissions(chat_id, new_perm)
            await message.reply(
                strings["unlocked_successfully"].format(lock=lock[0], chat=chat_title)
            )


async def lock_parser(chat_id, rev=False):
    keywords = {
        "all": "can_send_messages",
        "media": "can_send_media_messages",
        "polls": "can_send_polls",
        "others": "can_send_other_messages",
    }
    current_lock = (await bot.get_chat(chat_id)).permissions

    for lock, keyword in itertools.zip_longest(
        dict(current_lock).keys(), keywords.items()
    ):
        if keyword is not None and lock in keyword:
            if rev:
                lock = list([keyword[0], keyword[1]])
                status = not current_lock[keyword[1]]
            else:
                status = not current_lock[lock]
                lock = keyword[0]
            yield lock, status


__mod_name__ = "Locks"

__help__ = """
Use this feature to block users from sending specific message types to your group!
<b>Available commands are:</b>
- /locks or /locktypes: Use this command to know current state of your locks in your group!
- /lock (locktype): Locks a type of messages
- /unlock (locktype): Unlocks a type of message
"""
