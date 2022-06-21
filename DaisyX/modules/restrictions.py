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

import asyncio
import datetime  # noqa: F401
from contextlib import suppress

from aiogram.utils.exceptions import MessageNotModified
from babel.dates import format_timedelta

from DaisyX import BOT_ID, bot
from DaisyX.decorator import register
from DaisyX.services.redis import redis
from DaisyX.services.telethon import tbot

from .misc import customise_reason_finish, customise_reason_start
from .utils.connections import chat_connection
from .utils.language import get_strings_dec
from .utils.message import InvalidTimeUnit, convert_time, get_cmd
from .utils.restrictions import ban_user, kick_user, mute_user, unban_user, unmute_user
from .utils.user_details import (
    get_user_and_text_dec,
    get_user_dec,
    get_user_link,
    is_user_admin,
)


@register(
    cmds=["kick", "skick"],
    bot_can_restrict_members=True,
    user_can_restrict_members=True,
)
@chat_connection(admin=True, only_groups=True)
@get_user_and_text_dec()
@get_strings_dec("restrictions")
async def kick_user_cmd(message, chat, user, args, strings):
    chat_id = chat["chat_id"]
    user_id = user["user_id"]

    if user_id == BOT_ID:
        await message.reply(strings["kick_DaisyX"])
        return

    elif user_id == message.from_user.id:
        await message.reply(strings["kick_self"])
        return

    elif await is_user_admin(chat_id, user_id):
        await message.reply(strings["kick_admin"])
        return

    text = strings["user_kicked"].format(
        user=await get_user_link(user_id),
        admin=await get_user_link(message.from_user.id),
        chat_name=chat["chat_title"],
    )

    # Add reason
    if args:
        text += strings["reason"] % args

    # Check if silent
    silent = False
    if get_cmd(message) == "skick":
        silent = True
        key = f"leave_silent:{str(chat_id)}"
        redis.set(key, user_id)
        redis.expire(key, 30)
        text += strings["purge"]

    await kick_user(chat_id, user_id)

    msg = await message.reply(text)

    # Del msgs if silent
    if silent:
        to_del = [msg.message_id, message.message_id]
        if (
            "reply_to_message" in message
            and message.reply_to_message.from_user.id == user_id
        ):
            to_del.append(message.reply_to_message.message_id)
        await asyncio.sleep(5)
        await tbot.delete_messages(chat_id, to_del)


@register(
    cmds=["mute", "smute", "tmute", "stmute"],
    bot_can_restrict_members=True,
    user_can_restrict_members=True,
)
@chat_connection(admin=True, only_groups=True)
@get_user_and_text_dec()
@get_strings_dec("restrictions")
async def mute_user_cmd(message, chat, user, args, strings):
    chat_id = chat["chat_id"]
    user_id = user["user_id"]

    if user_id == BOT_ID:
        await message.reply(strings["mute_DaisyX"])
        return

    elif user_id == message.from_user.id:
        await message.reply(strings["mute_self"])
        return

    elif await is_user_admin(chat_id, user_id):
        await message.reply(strings["mute_admin"])
        return

    text = strings["user_muted"].format(
        user=await get_user_link(user_id),
        admin=await get_user_link(message.from_user.id),
        chat_name=chat["chat_title"],
    )

    curr_cmd = get_cmd(message)

    # Check if temprotary
    until_date = None
    if curr_cmd in ("tmute", "stmute"):
        if args is not None and len(args := args.split()) > 0:
            try:
                until_date = convert_time(args[0])
            except (InvalidTimeUnit, TypeError, ValueError):
                await message.reply(strings["invalid_time"])
                return

            text += strings["on_time"] % format_timedelta(
                until_date, locale=strings["language_info"]["babel"]
            )

            # Add reason
            if len(args) > 1:
                text += strings["reason"] % " ".join(args[1:])
        else:
            await message.reply(strings["enter_time"])
            return
    elif args is not None and len(args := args.split()) > 0:
        text += strings["reason"] % " ".join(args[:])

    # Check if silent
    silent = False
    if curr_cmd in ("smute", "stmute"):
        silent = True
        key = f"leave_silent:{str(chat_id)}"
        redis.set(key, user_id)
        redis.expire(key, 30)
        text += strings["purge"]

    await mute_user(chat_id, user_id, until_date=until_date)

    msg = await message.reply(text)

    # Del msgs if silent
    if silent:
        to_del = [msg.message_id, message.message_id]
        if (
            "reply_to_message" in message
            and message.reply_to_message.from_user.id == user_id
        ):
            to_del.append(message.reply_to_message.message_id)
        await asyncio.sleep(5)
        await tbot.delete_messages(chat_id, to_del)


@register(cmds="unmute", bot_can_restrict_members=True, user_can_restrict_members=True)
@chat_connection(admin=True, only_groups=True)
@get_user_dec()
@get_strings_dec("restrictions")
async def unmute_user_cmd(message, chat, user, strings):
    chat_id = chat["chat_id"]
    user_id = user["user_id"]

    if user_id == BOT_ID:
        await message.reply(strings["unmute_DaisyX"])
        return

    elif user_id == message.from_user.id:
        await message.reply(strings["unmute_self"])
        return

    elif await is_user_admin(chat_id, user_id):
        await message.reply(strings["unmute_admin"])
        return

    await unmute_user(chat_id, user_id)

    text = strings["user_unmuted"].format(
        user=await get_user_link(user_id),
        admin=await get_user_link(message.from_user.id),
        chat_name=chat["chat_title"],
    )

    await message.reply(text)


@register(
    cmds=["ban", "sban", "tban", "stban"],
    bot_can_restrict_members=True,
    user_can_restrict_members=True,
)
@chat_connection(admin=True, only_groups=True)
@get_user_and_text_dec()
@get_strings_dec("restrictions")
async def ban_user_cmd(message, chat, user, args, strings):
    chat_id = chat["chat_id"]
    user_id = user["user_id"]

    if user_id == BOT_ID:
        await message.reply(strings["ban_DaisyX"])
        return

    elif user_id == message.from_user.id:
        await message.reply(strings["ban_self"])
        return

    elif await is_user_admin(chat_id, user_id):
        await message.reply(strings["ban_admin"])
        return

    text = strings["user_banned"].format(
        user=await get_user_link(user_id),
        admin=await get_user_link(message.from_user.id),
        chat_name=chat["chat_title"],
    )

    curr_cmd = get_cmd(message)

    # Check if temprotary
    until_date = None
    if curr_cmd in ("tban", "stban"):
        if args is not None and len(args := args.split()) > 0:
            try:
                until_date = convert_time(args[0])
            except (InvalidTimeUnit, TypeError, ValueError):
                await message.reply(strings["invalid_time"])
                return

            text += strings["on_time"] % format_timedelta(
                until_date, locale=strings["language_info"]["babel"]
            )

            # Add reason
            if len(args) > 1:
                text += strings["reason"] % " ".join(args[1:])
        else:
            await message.reply(strings["enter_time"])
            return
    elif args is not None and len(args := args.split()) > 0:
        text += strings["reason"] % " ".join(args[:])

    # Check if silent
    silent = False
    if curr_cmd in ("sban", "stban"):
        silent = True
        key = f"leave_silent:{str(chat_id)}"
        redis.set(key, user_id)
        redis.expire(key, 30)
        text += strings["purge"]

    await ban_user(chat_id, user_id, until_date=until_date)

    msg = await message.reply(text)

    # Del msgs if silent
    if silent:
        to_del = [msg.message_id, message.message_id]
        if (
            "reply_to_message" in message
            and message.reply_to_message.from_user.id == user_id
        ):
            to_del.append(message.reply_to_message.message_id)
        await asyncio.sleep(5)
        await tbot.delete_messages(chat_id, to_del)


@register(cmds="unban", bot_can_restrict_members=True, user_can_restrict_members=True)
@chat_connection(admin=True, only_groups=True)
@get_user_dec()
@get_strings_dec("restrictions")
async def unban_user_cmd(message, chat, user, strings):
    chat_id = chat["chat_id"]
    user_id = user["user_id"]

    if user_id == BOT_ID:
        await message.reply(strings["unban_DaisyX"])
        return

    elif user_id == message.from_user.id:
        await message.reply(strings["unban_self"])
        return

    elif await is_user_admin(chat_id, user_id):
        await message.reply(strings["unban_admin"])
        return

    await unban_user(chat_id, user_id)

    text = strings["user_unband"].format(
        user=await get_user_link(user_id),
        admin=await get_user_link(message.from_user.id),
        chat_name=chat["chat_title"],
    )

    await message.reply(text)


@register(f="leave")
async def leave_silent(message):
    if message.from_user.id != BOT_ID:
        return

    if (
        redis.get(f"leave_silent:{str(message.chat.id)}")
        == message.left_chat_member.id
    ):
        await message.delete()


@get_strings_dec("restrictions")
async def filter_handle_ban(message, chat, data: dict, strings=None):
    if await is_user_admin(chat["chat_id"], message.from_user.id):
        return
    if await ban_user(chat["chat_id"], message.from_user.id):
        reason = data.get("reason", None) or strings["filter_action_rsn"]
        text = strings["filtr_ban_success"] % (
            await get_user_link(BOT_ID),
            await get_user_link(message.from_user.id),
            reason,
        )
        await bot.send_message(chat["chat_id"], text)


@get_strings_dec("restrictions")
async def filter_handle_mute(message, chat, data, strings=None):
    if await is_user_admin(chat["chat_id"], message.from_user.id):
        return
    if await mute_user(chat["chat_id"], message.from_user.id):
        reason = data.get("reason", None) or strings["filter_action_rsn"]
        text = strings["filtr_mute_success"] % (
            await get_user_link(BOT_ID),
            await get_user_link(message.from_user.id),
            reason,
        )
        await bot.send_message(chat["chat_id"], text)


@get_strings_dec("restrictions")
async def filter_handle_tmute(message, chat, data, strings=None):
    if await is_user_admin(chat["chat_id"], message.from_user.id):
        return
    if await mute_user(
        chat["chat_id"], message.from_user.id, until_date=eval(data["time"])
    ):
        reason = data.get("reason", None) or strings["filter_action_rsn"]
        time = format_timedelta(
            eval(data["time"]), locale=strings["language_info"]["babel"]
        )
        text = strings["filtr_tmute_success"] % (
            await get_user_link(BOT_ID),
            await get_user_link(message.from_user.id),
            time,
            reason,
        )
        await bot.send_message(chat["chat_id"], text)


@get_strings_dec("restrictions")
async def filter_handle_tban(message, chat, data, strings=None):
    if await is_user_admin(chat["chat_id"], message.from_user.id):
        return
    if await ban_user(
        chat["chat_id"], message.from_user.id, until_date=eval(data["time"])
    ):
        reason = data.get("reason", None) or strings["filter_action_rsn"]
        time = format_timedelta(
            eval(data["time"]), locale=strings["language_info"]["babel"]
        )
        text = strings["filtr_tban_success"] % (
            await get_user_link(BOT_ID),
            await get_user_link(message.from_user.id),
            time,
            reason,
        )
        await bot.send_message(chat["chat_id"], text)


@get_strings_dec("restrictions")
async def time_setup_start(message, strings):
    with suppress(MessageNotModified):
        await message.edit_text(strings["time_setup_start"])


@get_strings_dec("restrictions")
async def time_setup_finish(message, data, strings):
    try:
        time = convert_time(message.text)
    except (InvalidTimeUnit, TypeError, ValueError):
        await message.reply(strings["invalid_time"])
        return None
    else:
        return {"time": repr(time)}


@get_strings_dec("restrictions")
async def filter_handle_kick(message, chat, data, strings=None):
    if await is_user_admin(chat["chat_id"], message.from_user.id):
        return
    if await kick_user(chat["chat_id"], message.from_user.id):
        await bot.send_message(
            chat["chat_id"],
            strings["user_kicked"].format(
                user=await get_user_link(message.from_user.id),
                admin=await get_user_link(BOT_ID),
                chat_name=chat["chat_title"],
            ),
        )


__filters__ = {
    "ban_user": {
        "title": {"module": "restrictions", "string": "filter_title_ban"},
        "setup": {"start": customise_reason_start, "finish": customise_reason_finish},
        "handle": filter_handle_ban,
    },
    "mute_user": {
        "title": {"module": "restrictions", "string": "filter_title_mute"},
        "setup": {"start": customise_reason_start, "finish": customise_reason_finish},
        "handle": filter_handle_mute,
    },
    "tmute_user": {
        "title": {"module": "restrictions", "string": "filter_title_tmute"},
        "handle": filter_handle_tmute,
        "setup": [
            {"start": time_setup_start, "finish": time_setup_finish},
            {"start": customise_reason_start, "finish": customise_reason_finish},
        ],
    },
    "tban_user": {
        "title": {"module": "restrictions", "string": "filter_title_tban"},
        "handle": filter_handle_tban,
        "setup": [
            {"start": time_setup_start, "finish": time_setup_finish},
            {"start": customise_reason_start, "finish": customise_reason_finish},
        ],
    },
    "kick_user": {
        "title": {"module": "restrictions", "string": "filter_title_kick"},
        "handle": filter_handle_kick,
    },
}


__mod_name__ = "Restrictions"

__help__ = """
General admin's rights is restrict users and control their rules with this module you can easely do it.

<b>Available commands:</b>
<b>Kicks:</b>
- /kick: Kicks a user
- /skick: Silently kicks

<b>Mutes:</b>
- /mute: Mutes a user
- /smute: Silently mutes
- /tmute (time): Temprotary mute a user
- /stmute (time): Silently temprotary mute a user
- /unmute: Unmutes the user

<b>Bans:</b>
- /ban: Bans a user
- /sban: Silently bans
- /tban (time): Temprotary ban a user
-/stban (time): Silently temprotary ban a user
- /unban: Unbans the user

<b>Examples:</b>
<code>- Mute a user for two hours.
-> /tmute @username 2h</code>


"""
