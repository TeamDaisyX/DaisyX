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


import functools
import re
from contextlib import suppress

from aiogram.types import Message
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.deep_linking import get_start_link
from aiogram.utils.exceptions import MessageNotModified
from babel.dates import format_timedelta
from bson.objectid import ObjectId

from DaisyX import BOT_ID, bot
from DaisyX.decorator import register
from DaisyX.services.mongo import db
from DaisyX.services.telethon import tbot

from .misc import customise_reason_finish, customise_reason_start
from .utils.connections import chat_connection
from .utils.language import get_strings_dec
from .utils.message import InvalidTimeUnit, convert_time
from .utils.restrictions import ban_user, mute_user
from .utils.user_details import (
    get_user_and_text_dec,
    get_user_dec,
    get_user_link,
    is_user_admin,
)


@register(cmds="warn", user_can_restrict_members=True, bot_can_restrict_members=True)
@chat_connection(admin=True, only_groups=True)
@get_user_and_text_dec()
async def warn_cmd(message, chat, user, text):
    await warn_func(message, chat, user, text)


@register(cmds="dwarn", user_can_restrict_members=True, bot_can_restrict_members=True)
@chat_connection(admin=True, only_groups=True)
@get_user_and_text_dec()
async def warn_cmd(message, chat, user, text):
    if not message.reply_to_message:
        await message.reply(strings["reply_to_msg"])
        return
    await warn_func(message, chat, user, text)
    msgs = [message.message_id, message.reply_to_message.message_id]
    await tbot.delete_messages(message.chat.id, msgs)


@get_strings_dec("warns")
async def warn_func(message: Message, chat, user, text, strings, filter_action=False):
    chat_id = chat["chat_id"]
    chat_title = chat["chat_title"]
    by_id = BOT_ID if filter_action is True else message.from_user.id
    user_id = user["user_id"] if filter_action is False else user

    if user_id == BOT_ID:
        await message.reply(strings["warn_sofi"])
        return

    if not filter_action:
        if user_id == message.from_user.id:
            await message.reply(strings["warn_self"])
            return

    if await is_user_admin(chat_id, user_id):
        if not filter_action:
            await message.reply(strings["warn_admin"])
        return

    reason = text
    warn_id = str(
        (
            await db.warns.insert_one(
                {
                    "user_id": user_id,
                    "chat_id": chat_id,
                    "reason": str(reason),
                    "by": by_id,
                }
            )
        ).inserted_id
    )

    admin = await get_user_link(by_id)
    member = await get_user_link(user_id)
    text = strings["warn"].format(admin=admin, user=member, chat_name=chat_title)

    if reason:
        text += strings["warn_rsn"].format(reason=reason)

    warns_count = await db.warns.count_documents(
        {"chat_id": chat_id, "user_id": user_id}
    )

    buttons = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            "⚠️ Remove warn", callback_data="remove_warn_{}".format(warn_id)
        )
    )

    if await db.rules.find_one({"chat_id": chat_id}):
        buttons.insert(
            InlineKeyboardButton(
                "📝 Rules", url=await get_start_link(f"btn_rules_{chat_id}")
            )
        )

    if warn_limit := await db.warnlimit.find_one({"chat_id": chat_id}):
        max_warn = int(warn_limit["num"])
    else:
        max_warn = 3

    if filter_action:
        action = functools.partial(bot.send_message, chat_id=chat_id)
    elif message.reply_to_message:
        action = message.reply_to_message.reply
    else:
        action = functools.partial(message.reply, disable_notification=True)

    if warns_count >= max_warn:
        if await max_warn_func(chat_id, user_id):
            await db.warns.delete_many({"user_id": user_id, "chat_id": chat_id})
            data = await db.warnmode.find_one({"chat_id": chat_id})
            if data is not None:
                if data["mode"] == "tmute":
                    text = strings["max_warn_exceeded:tmute"].format(
                        user=member,
                        time=format_timedelta(
                            convert_time(data["time"]),
                            locale=strings["language_info"]["babel"],
                        ),
                    )
                else:
                    text = strings["max_warn_exceeded"].format(
                        user=member,
                        action=strings["banned"]
                        if data["mode"] == "ban"
                        else strings["muted"],
                    )
                return await action(text=text)
            return await action(
                text=strings["max_warn_exceeded"].format(
                    user=member, action=strings["banned"]
                )
            )
    text += strings["warn_num"].format(curr_warns=warns_count, max_warns=max_warn)
    return await action(text=text, reply_markup=buttons, disable_web_page_preview=True)


@register(
    regexp=r"remove_warn_(.*)",
    f="cb",
    allow_kwargs=True,
    user_can_restrict_members=True,
)
@get_strings_dec("warns")
async def rmv_warn_btn(event, strings, regexp=None, **kwargs):
    warn_id = ObjectId(re.search(r"remove_warn_(.*)", str(regexp)).group(1)[:-2])
    user_id = event.from_user.id
    admin_link = await get_user_link(user_id)
    await db.warns.delete_one({"_id": warn_id})
    with suppress(MessageNotModified):
        await event.message.edit_text(
            strings["warn_btn_rmvl_success"].format(admin=admin_link)
        )


@register(cmds="warns")
@chat_connection(admin=True, only_groups=True)
@get_user_dec(allow_self=True)
@get_strings_dec("warns")
async def warns(message, chat, user, strings):
    chat_id = chat["chat_id"]
    user_id = user["user_id"]
    text = strings["warns_header"]
    user_link = await get_user_link(user_id)

    count = 0
    async for warn in db.warns.find({"user_id": user_id, "chat_id": chat_id}):
        count += 1
        by = await get_user_link(warn["by"])
        rsn = warn["reason"]
        reason = f"<code>{rsn}</code>"
        if not rsn or rsn == "None":
            reason = "<i>No Reason</i>"
        text += strings["warns"].format(count=count, reason=reason, admin=by)

    if count == 0:
        await message.reply(strings["no_warns"].format(user=user_link))
        return

    await message.reply(text, disable_notification=True)


@register(cmds="warnlimit", user_admin=True)
@chat_connection(admin=True, only_groups=True)
@get_strings_dec("warns")
async def warnlimit(message, chat, strings):
    chat_id = chat["chat_id"]
    chat_title = chat["chat_title"]
    arg = message.get_args().split()

    if not arg:
        if current_limit := await db.warnlimit.find_one({"chat_id": chat_id}):
            num = current_limit["num"]
        else:
            num = 3  # Default value
        await message.reply(strings["warn_limit"].format(chat_name=chat_title, num=num))
    elif not arg[0].isdigit():
        return await message.reply(strings["not_digit"])
    else:
        if int(arg[0]) < 2:
            return await message.reply(strings["warnlimit_short"])

        elif int(arg[0]) > 10000:  # Max value
            return await message.reply(strings["warnlimit_long"])

        new = {"chat_id": chat_id, "num": int(arg[0])}

        await db.warnlimit.update_one({"chat_id": chat_id}, {"$set": new}, upsert=True)
        await message.reply(strings["warnlimit_updated"].format(num=int(arg[0])))


@register(cmds=["resetwarns", "delwarns"], user_can_restrict_members=True)
@chat_connection(admin=True, only_groups=True)
@get_user_dec()
@get_strings_dec("warns")
async def reset_warn(message, chat, user, strings):
    chat_id = chat["chat_id"]
    chat_title = chat["chat_title"]
    user_id = user["user_id"]
    user_link = await get_user_link(user_id)
    admin_link = await get_user_link(message.from_user.id)

    if user_id == BOT_ID:
        await message.reply(strings["rst_wrn_sofi"])
        return

    if await db.warns.find_one({"chat_id": chat_id, "user_id": user_id}):
        deleted = await db.warns.delete_many({"chat_id": chat_id, "user_id": user_id})
        purged = deleted.deleted_count
        await message.reply(
            strings["purged_warns"].format(
                admin=admin_link, num=purged, user=user_link, chat_title=chat_title
            )
        )
    else:
        await message.reply(strings["usr_no_wrn"].format(user=user_link))


@register(
    cmds=["warnmode", "warnaction"], user_admin=True, bot_can_restrict_members=True
)
@chat_connection(admin=True)
@get_strings_dec("warns")
async def warnmode(message, chat, strings):
    chat_id = chat["chat_id"]
    acceptable_args = ["ban", "tmute", "mute"]
    arg = str(message.get_args()).split()
    new = {"chat_id": chat_id}

    if arg and arg[0] in acceptable_args:
        option = "".join(arg[0])
        if (
            data := await db.warnmode.find_one({"chat_id": chat_id})
        ) is not None and data["mode"] == option:
            return await message.reply(strings["same_mode"])
        if arg[0] == acceptable_args[0]:
            new["mode"] = option
            await db.warnmode.update_one(
                {"chat_id": chat_id}, {"$set": new}, upsert=True
            )
        elif arg[0] == acceptable_args[1]:
            try:
                time = arg[1]
            except IndexError:
                return await message.reply(strings["no_time"])
            else:
                try:
                    # TODO: For better UX we have to show until time of tmute when action is done.
                    # We can't store timedelta class in mongodb; Here we check validity of given time.
                    convert_time(time)
                except (InvalidTimeUnit, TypeError, ValueError):
                    return await message.reply(strings["invalid_time"])
                else:
                    new.update(mode=option, time=time)
                    await db.warnmode.update_one(
                        {"chat_id": chat_id}, {"$set": new}, upsert=True
                    )
        elif arg[0] == acceptable_args[2]:
            new["mode"] = option
            await db.warnmode.update_one(
                {"chat_id": chat_id}, {"$set": new}, upsert=True
            )
        await message.reply(strings["warnmode_success"] % (chat["chat_title"], option))
    else:
        text = ""
        if (curr_mode := await db.warnmode.find_one({"chat_id": chat_id})) is not None:
            mode = curr_mode["mode"]
            text += strings["mode_info"] % mode
        text += strings["wrng_args"]
        text += "\n".join([f"- {i}" for i in acceptable_args])
        await message.reply(text)


async def max_warn_func(chat_id, user_id):
    if (data := await db.warnmode.find_one({"chat_id": chat_id})) is not None:
        if data["mode"] == "ban":
            return await ban_user(chat_id, user_id)
        elif data["mode"] == "tmute":
            time = convert_time(data["time"])
            return await mute_user(chat_id, user_id, time)
        elif data["mode"] == "mute":
            return await mute_user(chat_id, user_id)
    else:  # Default
        return await ban_user(chat_id, user_id)


async def __export__(chat_id):
    if data := await db.warnlimit.find_one({"chat_id": chat_id}):
        number = data["num"]
    else:
        number = 3

    if warnmode_data := await db.warnmode.find_one({"chat_id": chat_id}):
        del warnmode_data["chat_id"], warnmode_data["_id"]
    else:
        warnmode_data = None

    return {"warns": {"warns_limit": number, "warn_mode": warnmode_data}}


async def __import__(chat_id, data):
    if "warns_limit" in data:
        number = data["warns_limit"]
        if number < 2:
            return

        elif number > 10000:  # Max value
            return

        await db.warnlimit.update_one(
            {"chat_id": chat_id}, {"$set": {"num": number}}, upsert=True
        )

    if (data := data["warn_mode"]) is not None:
        await db.warnmode.update_one({"chat_id": chat_id}, {"$set": data}, upsert=True)


@get_strings_dec("warns")
async def filter_handle(message, chat, data, string=None):
    if await is_user_admin(chat["chat_id"], message.from_user.id):
        return
    target_user = message.from_user.id
    text = data.get("reason", None) or string["filter_handle_rsn"]
    await warn_func(message, chat, target_user, text, filter_action=True)


__filters__ = {
    "warn_user": {
        "title": {"module": "warns", "string": "filters_title"},
        "setup": {"start": customise_reason_start, "finish": customise_reason_finish},
        "handle": filter_handle,
    }
}


__mod_name__ = "Warnings"

__help__ = """
You can keep your members from getting out of control using this feature!

<b>Available commands:</b>
<b>General (Admins):</b>
- /warn (?user) (?reason): Use this command to warn the user! you can mention or reply to the offended user and add reason if needed
- /delwarns or /resetwarns: This command is used to delete all the warns user got so far in the chat
- /dwarn [reply]: Delete the replied message and warn him
<b>Warnlimt (Admins):</b>
- /warnlimit (new limit): Sets a warnlimit
Not all chats want to give same maximum warns to the user, right? This command will help you to modify default maximum warns. Default is 3

The warnlimit should be greater than <code>1</code> and less than <code>10,000</code>

<b>Warnaction (Admins):</b>
/warnaction (mode) (?time)
Well again, not all chats want to ban (default) users when exceed maximum warns so this command will able to modify that.
Current supported actions are <code>ban</code> (default one), <code>mute</code>, <code>tmute</code>. The tmute mode require <code>time</code> argument as you guessed.

<b>Available for all users:</b>
/warns (?user)
Use this command to know number of warns and information about warns you got so far in the chat. To use yourself you doesn't require user argument.
"""
