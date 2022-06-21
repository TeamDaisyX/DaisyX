# Copyright (C) 2018 - 2020 MrYacha. All rights reserved. Source code available under the AGPL.
# Copyright (C) 2021 TeamDaisyX
# Copyright (C) 2020 Inuka Asith

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

import re

from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import CallbackQuery
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.deep_linking import get_start_link
from aiogram.utils.exceptions import BotBlocked, CantInitiateConversation

from DaisyX import bot
from DaisyX.decorator import register
from DaisyX.services.mongo import db
from DaisyX.services.redis import redis

from .utils.connections import chat_connection, get_connection_data, set_connected_chat
from .utils.language import get_strings_dec
from .utils.message import get_arg
from .utils.notes import BUTTONS
from .utils.user_details import get_chat_dec, is_user_admin

connect_to_chat_cb = CallbackData("connect_to_chat_cb", "chat_id")


@get_strings_dec("connections")
async def def_connect_chat(message, user_id, chat_id, chat_title, strings, edit=False):
    await set_connected_chat(user_id, chat_id)

    text = strings["pm_connected"].format(chat_name=chat_title)
    if edit:
        await message.edit_text(text)
    else:
        await message.reply(text)


# In chat - connect directly to chat
@register(cmds="connect", only_groups=True, no_args=True)
@get_strings_dec("connections")
async def connect_to_chat_direct(message, strings):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id == 1087968824:
        # just warn the user that connections with admin rights doesn't work
        return await message.reply(
            strings["anon_admin_conn"],
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(
                    strings["click_here"], callback_data="anon_conn_cb"
                )
            ),
        )

    chat = await db.chat_list.find_one({"chat_id": chat_id})
    chat_title = chat["chat_title"] if chat is not None else message.chat.title
    text = strings["pm_connected"].format(chat_name=chat_title)

    try:
        await bot.send_message(user_id, text)
        await def_connect_chat(message, user_id, chat_id, chat_title)
    except (BotBlocked, CantInitiateConversation):
        await message.reply(strings["connected_pm_to_me"].format(chat_name=chat_title))
        redis.set(f"DaisyX_connected_start_state:{str(user_id)}", 1)


# In pm without args - show last connected chats
@register(cmds="connect", no_args=True, only_pm=True)
@get_strings_dec("connections")
@chat_connection()
async def connect_chat_keyboard(message, strings, chat):
    connected_data = await get_connection_data(message.from_user.id)
    if not connected_data:
        return await message.reply(strings["u_wasnt_connected"])

    if chat["status"] != "private":
        text = strings["connected_chat"].format(chat_name=chat["chat_title"])
    elif "command" in connected_data:
        if chat := await db.chat_list.find_one({"chat_id": connected_data["chat_id"]}):
            chat_title = chat["chat_title"]
        else:
            chat_title = connected_data["chat_id"]
        text = strings["connected_chat:cmds"].format(
            chat_name=chat_title,
            # disconnect is builtin command, should not be shown
            commands=", ".join(
                f"<code>/{cmd}</code>"
                for cmd in connected_data["command"]
                if cmd != "disconnect"
            ),
        )
    else:
        text = ""

    text += strings["select_chat_to_connect"]
    markup = InlineKeyboardMarkup(row_width=1)
    for chat_id in reversed(connected_data["history"][-3:]):
        chat = await db.chat_list.find_one({"chat_id": chat_id})
        markup.insert(
            InlineKeyboardButton(
                chat["chat_title"],
                callback_data=connect_to_chat_cb.new(chat_id=chat_id),
            )
        )

    await message.reply(text, reply_markup=markup)


# Callback for prev. function
@register(connect_to_chat_cb.filter(), f="cb", allow_kwargs=True)
async def connect_chat_keyboard_cb(message, callback_data=False, **kwargs):
    chat_id = int(callback_data["chat_id"])
    chat = await db.chat_list.find_one({"chat_id": chat_id})
    await def_connect_chat(
        message.message, message.from_user.id, chat_id, chat["chat_title"], edit=True
    )


# In pm with args - connect to chat by arg
@register(cmds="connect", has_args=True, only_pm=True)
@get_chat_dec()
@get_strings_dec("connections")
async def connect_to_chat_from_arg(message, chat, strings):
    user_id = message.from_user.id
    chat_id = chat["chat_id"]

    arg = get_arg(message)
    if arg.startswith("-"):
        chat_id = int(arg)

    if not chat_id:
        await message.reply(strings["cant_find_chat_use_id"])
        return

    await def_connect_chat(message, user_id, chat_id, chat["chat_title"])


@register(cmds="disconnect", only_pm=True)
@get_strings_dec("connections")
async def disconnect_from_chat_direct(message, strings):
    if (data := await get_connection_data(message.from_user.id)) and "chat_id" in data:
        chat = await db.chat_list.find_one({"chat_id": data["chat_id"]})
        user_id = message.from_user.id
        await set_connected_chat(user_id, None)
        await message.reply(
            strings["disconnected"].format(chat_name=chat["chat_title"])
        )


@register(cmds="allowusersconnect")
@get_strings_dec("connections")
@chat_connection(admin=True, only_groups=True)
async def allow_users_to_connect(message, strings, chat):
    chat_id = chat["chat_id"]
    arg = get_arg(message).lower()
    if not arg:
        status = strings["enabled"]
        data = await db.chat_connection_settings.find_one({"chat_id": chat_id})
        if (
            data
            and "allow_users_connect" in data
            and data["allow_users_connect"] is False
        ):
            status = strings["disabled"]
        await message.reply(
            strings["chat_users_connections_info"].format(
                status=status, chat_name=chat["chat_title"]
            )
        )
        return
    enable = ("enable", "on", "ok", "yes")
    disable = ("disable", "off", "no")
    if arg in enable:
        r_bool = True
        status = strings["enabled"]
    elif arg in disable:
        r_bool = False
        status = strings["disabled"]
    else:
        await message.reply(strings["bad_arg_bool"])
        return

    await db.chat_connection_settings.update_one(
        {"chat_id": chat_id}, {"$set": {"allow_users_connect": r_bool}}, upsert=True
    )
    await message.reply(
        strings["chat_users_connections_cng"].format(
            status=status, chat_name=chat["chat_title"]
        )
    )


@register(cmds="start", only_pm=True)
@get_strings_dec("connections")
@chat_connection()
async def connected_start_state(message, strings, chat):
    key = f"DaisyX_connected_start_state:{str(message.from_user.id)}"
    if redis.get(key):
        await message.reply(
            strings["pm_connected"].format(chat_name=chat["chat_title"])
        )
        redis.delete(key)


BUTTONS.update({"connect": "btn_connect_start"})


@register(CommandStart(re.compile(r"btn_connect_start")), allow_kwargs=True)
@get_strings_dec("connections")
async def connect_start(message, strings, regexp=None, **kwargs):
    args = message.get_args().split("_")

    # In case if button have arg it will be used. # TODO: Check chat_id, parse chat nickname.
    arg = args[3]

    if arg.startswith("-") or arg.isdigit():
        chat = await db.chat_list.find_one({"chat_id": int(arg)})
    elif arg.startswith("@"):
        chat = await db.chat_list.find_one({"chat_nick": arg.lower()})
    else:
        await message.reply(strings["cant_find_chat_use_id"])
        return

    await def_connect_chat(
        message, message.from_user.id, chat["chat_id"], chat["chat_title"]
    )


@register(regexp="anon_conn_cb", f="cb")
async def connect_anon_admins(event: CallbackQuery):
    if not await is_user_admin(event.message.chat.id, event.from_user.id):
        return

    if (
        event.message.chat.id
        not in (data := await db.user_list.find_one({"user_id": event.from_user.id}))[
            "chats"
        ]
    ):
        await db.user_list.update_one(
            {"_id": data["_id"]}, {"$addToSet": {"chats": event.message.chat.id}}
        )
    return await event.answer(
        url=await get_start_link(f"btn_connect_start_{event.message.chat.id}")
    )


__mod_name__ = "Connections"

__help__ = """
Sometimes you need change something in your chat, like notes, but you don't want to spam in it, try connections, this allow you change chat settings and manage chat's content in personal message with Daisy.

<b>Available commands are:</b>
<b>Avaible only in PM:</b>
- /connect: Show last connected chats button for fast connection
- /connect (chat ID or chat nickname): Connect to chat by argument which you provided
- /reconnect: Connect to last connected chat before
- /disconnect: Disconnect from

<b>Avaible only in groups:</b>
- /connect: Direct connect to this group

<b>Other commands:</b>
- /allowusersconnect (on/off enable/disable): Enable or disable connection feature for regular users, for admins connections will be works always
"""
