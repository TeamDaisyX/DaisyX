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

import html

from aiogram.utils.exceptions import ChatAdminRequired
from telethon.errors import AdminRankEmojiNotAllowedError

from DaisyX import BOT_ID, bot
from DaisyX.decorator import register
from DaisyX.services.telethon import tbot

from .utils.connections import chat_connection
from .utils.language import get_strings_dec
from .utils.user_details import (
    get_admins_rights,
    get_user_and_text_dec,
    get_user_dec,
    get_user_link,
)


@register(cmds="promote", bot_can_promote_members=True, user_can_promote_members=True)
@chat_connection(admin=True, only_groups=True)
@get_user_and_text_dec()
@get_strings_dec("promotes")
async def promote(message, chat, user, args, strings):
    chat_id = chat["chat_id"]
    text = strings["promote_success"].format(
        user=await get_user_link(user["user_id"]), chat_name=chat["chat_title"]
    )

    if user["user_id"] == BOT_ID:
        return

    if user["user_id"] == message.from_user.id:
        return await message.reply(strings["cant_promote_yourself"])

    title = None

    if args:
        if len(args) > 16:
            await message.reply(strings["rank_to_loong"])
            return
        title = args
        text += strings["promote_title"].format(role=html.escape(title, quote=False))

    try:
        await tbot.edit_admin(
            chat_id,
            user["user_id"],
            invite_users=True,
            change_info=True,
            ban_users=True,
            delete_messages=True,
            pin_messages=True,
            title=title,
        )
    except ValueError:
        return await message.reply(strings["cant_get_user"])
    except AdminRankEmojiNotAllowedError:
        return await message.reply(strings["emoji_not_allowed"])
    await get_admins_rights(chat_id, force_update=True)  # Reset a cache
    await message.reply(text)


@register(cmds="demote", bot_can_promote_members=True, user_can_promote_members=True)
@chat_connection(admin=True, only_groups=True)
@get_user_dec()
@get_strings_dec("promotes")
async def demote(message, chat, user, strings):
    chat_id = chat["chat_id"]
    if user["user_id"] == BOT_ID:
        return

    try:
        await bot.promote_chat_member(chat_id, user["user_id"])
    except ChatAdminRequired:
        return await message.reply(strings["demote_failed"])

    await get_admins_rights(chat_id, force_update=True)  # Reset a cache
    await message.reply(
        strings["demote_success"].format(
            user=await get_user_link(user["user_id"]), chat_name=chat["chat_title"]
        )
    )


__mod_name__ = "Admin"

__help__ = """
Make it easy to promote and demote users with the admin module!

<b>Available commands:</b>
- /promote (user) (?admin's title): Promotes the user to admin.
- /demote (user): Demotes the user from admin.
- /adminlist: Shows all admins of the chat.
- /admincache: Update the admin cache, to take into account new admins/admin permissions.
- /ban: bans a user
- /unban: unbans a user
- /mute: mute a user
- /unmute: unmutes a user
- /tban [entity] : temporarily bans a user for the time interval.
- /tmute [entity] : temporarily mutes a user for the time interval.
- /kick: kicks a user
- /kickme: kicks yourself (non-admins)
- /banme: bans yourself (non-admins)
- /settitle [entity] [title]: sets a custom title for an admin. If no [title] provided defaults to "Admin"
- /setdescription [text]: set group description
- /setgrouptitle [text] set group title
- /setgrouppic: reply to an image to set as group photo
- /setsticker: reply to a sticker pack to set as group stickers
- /purge: deletes all messages from the message you replied to
- /del: deletes the message replied to
- /lock [item(s)]: lock the usage of "item" for non-admins
- /unlock [item(s)]: unlock "item". Everyone can use them again
- /locks: gives the lock status of the chat
- /locktypes: gets a list of all things that can be locked
- /unbanall: Unbans all in the chat
- /unmuteall: Unmutes all in the chat
- /users: list all the users in the chat
- /zombies: counts the number of deleted account in your group
- /kickthefools: kicks all members inactive from 1 week
Example:
Sometimes, you promote or demote an admin manually, and Daisy doesn't realise it immediately. This is because to avoid spamming telegram servers, admin status is cached locally.
This means that you sometimes have to wait a few minutes for admin rights to update. If you want to update them immediately, you can use the /admincache command; that'll force Daisy to check who the admins are again.

<i> Special credits to Julia Project </i>
"""
