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
import csv
import html
import io
import os
import re
import time
import uuid
from contextlib import suppress
from datetime import datetime, timedelta
from typing import Optional

import babel
import rapidjson
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InputFile, Message
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import (
    ChatNotFound,
    NeedAdministratorRightsInTheChannel,
    Unauthorized,
)
from babel.dates import format_timedelta
from pymongo import DeleteMany, InsertOne

from DaisyX import BOT_ID, OPERATORS, OWNER_ID, bot, decorator
from DaisyX.services.mongo import db
from DaisyX.services.redis import redis
from DaisyX.services.telethon import tbot

from ..utils.cached import cached
from .utils.connections import chat_connection, get_connected_chat
from .utils.language import get_string, get_strings, get_strings_dec
from .utils.message import get_cmd, need_args_dec
from .utils.restrictions import ban_user, unban_user
from .utils.user_details import (
    check_admin_rights,
    get_chat_dec,
    get_user_and_text,
    get_user_link,
    is_chat_creator,
    is_user_admin,
)


class ImportFbansFileWait(StatesGroup):
    waiting = State()


delfed_cb = CallbackData("delfed_cb", "fed_id", "creator_id")


# functions


async def get_fed_f(message):
    chat = await get_connected_chat(message, admin=True)
    if "err_msg" not in chat:
        if chat["status"] == "private":
            # return fed which user is created
            fed = await get_fed_by_creator(chat["chat_id"])
        else:
            fed = await db.feds.find_one({"chats": {"$in": [chat["chat_id"]]}})
        if not fed:
            return False
        return fed


async def fed_post_log(fed, text):
    if "log_chat_id" not in fed:
        return
    chat_id = fed["log_chat_id"]
    with suppress(Unauthorized, NeedAdministratorRightsInTheChannel, ChatNotFound):
        await bot.send_message(chat_id, text)


# decorators


def get_current_chat_fed(func):
    async def wrapped_1(*args, **kwargs):
        message = args[0]
        real_chat_id = message.chat.id
        if not (fed := await get_fed_f(message)):
            await message.reply(
                await get_string(real_chat_id, "feds", "chat_not_in_fed")
            )
            return

        return await func(*args, fed, **kwargs)

    return wrapped_1


def get_fed_user_text(skip_no_fed=False, self=False):
    def wrapped(func):
        async def wrapped_1(*args, **kwargs):
            fed = None
            message = args[0]
            real_chat_id = message.chat.id
            user, text = await get_user_and_text(message)
            strings = await get_strings(real_chat_id, "feds")

            # Check non exits user
            data = message.get_args().split(" ")
            if (
                not user
                and len(data) > 0
                and data[0].isdigit()
                and int(data[0]) <= 2147483647
            ):
                user = {"user_id": int(data[0])}
                text = " ".join(data[1:]) if len(data) > 1 else None
            elif not user:
                if self is True:
                    user = await db.user_list.find_one(
                        {"user_id": message.from_user.id}
                    )
                else:
                    await message.reply(strings["cant_get_user"])
                    # Passing 'None' user will throw err
                    return

            # Check fed_id in args
            if text:
                text_args = text.split(" ", 1)
                if len(text_args) >= 1:
                    if text_args[0].count("-") == 4:
                        text = text_args[1] if len(text_args) > 1 else ""
                        if not (fed := await get_fed_by_id(text_args[0])):
                            await message.reply(strings["fed_id_invalid"])
                            return
                    else:
                        text = " ".join(text_args)

            if not fed:
                if not (fed := await get_fed_f(message)):
                    if not skip_no_fed:
                        await message.reply(strings["chat_not_in_fed"])
                        return
                    else:
                        fed = None

            return await func(*args, fed, user, text, **kwargs)

        return wrapped_1

    return wrapped


def get_fed_dec(func):
    async def wrapped_1(*args, **kwargs):
        fed = None
        message = args[0]
        real_chat_id = message.chat.id

        if message.text:
            text_args = message.text.split(" ", 2)
            if not len(text_args) < 2 and text_args[1].count("-") == 4:
                if not (fed := await get_fed_by_id(text_args[1])):
                    await message.reply(
                        await get_string(real_chat_id, "feds", "fed_id_invalid")
                    )
                    return

        # Check whether fed is still None; This will allow above fed variable to be passed
        # TODO(Better handling?)
        if fed is None:
            if not (fed := await get_fed_f(message)):
                await message.reply(
                    await get_string(real_chat_id, "feds", "chat_not_in_fed")
                )
                return

        return await func(*args, fed, **kwargs)

    return wrapped_1


def is_fed_owner(func):
    async def wrapped_1(*args, **kwargs):
        message = args[0]
        fed = args[1]
        user_id = message.from_user.id

        # check on anon
        if user_id in [1087968824, 777000]:
            return

        if not user_id == fed["creator"] and user_id != OWNER_ID:
            text = (await get_string(message.chat.id, "feds", "need_fed_admin")).format(
                name=html.escape(fed["fed_name"], False)
            )
            await message.reply(text)
            return

        return await func(*args, **kwargs)

    return wrapped_1


def is_fed_admin(func):
    async def wrapped_1(*args, **kwargs):
        message = args[0]
        fed = args[1]
        user_id = message.from_user.id

        # check on anon
        if user_id in [1087968824, 777000]:
            return

        if not user_id == fed["creator"] and user_id != OWNER_ID:
            if "admins" not in fed or user_id not in fed["admins"]:
                text = (
                    await get_string(message.chat.id, "feds", "need_fed_admin")
                ).format(name=html.escape(fed["fed_name"], False))
                return await message.reply(text)

        return await func(*args, **kwargs)

    return wrapped_1


# cmds


@decorator.register(cmds=["newfed", "fnew"])
@need_args_dec()
@get_strings_dec("feds")
async def new_fed(message, strings):
    fed_name = html.escape(message.get_args())
    user_id = message.from_user.id
    # dont support creation of newfed as anon admin
    if user_id == 1087968824:
        return await message.reply(strings["disallow_anon"])

    if not fed_name:
        await message.reply(strings["no_args"])

    if len(fed_name) > 60:
        await message.reply(strings["fed_name_long"])
        return

    if await get_fed_by_creator(user_id) and not user_id == OWNER_ID:
        await message.reply(strings["can_only_1_fed"])
        return

    if await db.feds.find_one({"fed_name": fed_name}):
        await message.reply(strings["name_not_avaible"].format(name=fed_name))
        return

    data = {"fed_name": fed_name, "fed_id": str(uuid.uuid4()), "creator": user_id}
    await db.feds.insert_one(data)
    await get_fed_by_id.reset_cache(data["fed_id"])
    await get_fed_by_creator.reset_cache(data["creator"])
    await message.reply(
        strings["created_fed"].format(
            name=fed_name, id=data["fed_id"], creator=await get_user_link(user_id)
        )
    )


@decorator.register(cmds=["joinfed", "fjoin"])
@need_args_dec()
@chat_connection(admin=True, only_groups=True)
@get_strings_dec("feds")
async def join_fed(message, chat, strings):
    fed_id = message.get_args().split(" ")[0]
    user_id = message.from_user.id
    chat_id = chat["chat_id"]

    if not await is_chat_creator(message, chat_id, user_id):
        await message.reply(strings["only_creators"])
        return

    # Assume Fed ID invalid
    if not (fed := await get_fed_by_id(fed_id)):
        await message.reply(strings["fed_id_invalid"])
        return

    # Assume chat already joined this/other fed
    if "chats" in fed and chat_id in fed["chats"]:
        await message.reply(strings["joined_fed_already"])
        return

    await db.feds.update_one(
        {"_id": fed["_id"]}, {"$addToSet": {"chats": {"$each": [chat_id]}}}
    )
    await get_fed_by_id.reset_cache(fed["fed_id"])
    await message.reply(
        strings["join_fed_success"].format(
            chat=chat["chat_title"], fed=html.escape(fed["fed_name"], False)
        )
    )
    await fed_post_log(
        fed,
        strings["join_chat_fed_log"].format(
            fed_name=fed["fed_name"],
            fed_id=fed["fed_id"],
            chat_name=chat["chat_title"],
            chat_id=chat_id,
        ),
    )


@decorator.register(cmds=["leavefed", "fleave"])
@chat_connection(admin=True, only_groups=True)
@get_current_chat_fed
@get_strings_dec("feds")
async def leave_fed_comm(message, chat, fed, strings):
    user_id = message.from_user.id
    if not await is_chat_creator(message, chat["chat_id"], user_id):
        await message.reply(strings["only_creators"])
        return

    await db.feds.update_one({"_id": fed["_id"]}, {"$pull": {"chats": chat["chat_id"]}})
    await get_fed_by_id.reset_cache(fed["fed_id"])
    await message.reply(
        strings["leave_fed_success"].format(
            chat=chat["chat_title"], fed=html.escape(fed["fed_name"], False)
        )
    )

    await fed_post_log(
        fed,
        strings["leave_chat_fed_log"].format(
            fed_name=html.escape(fed["fed_name"], False),
            fed_id=fed["fed_id"],
            chat_name=chat["chat_title"],
            chat_id=chat["chat_id"],
        ),
    )


@decorator.register(cmds="fsub")
@need_args_dec()
@get_current_chat_fed
@is_fed_owner
@get_strings_dec("feds")
async def fed_sub(message, fed, strings):
    fed_id = message.get_args().split(" ")[0]

    # Assume Fed ID is valid
    if not (fed2 := await get_fed_by_id(fed_id)):
        await message.reply(strings["fed_id_invalid"])
        return

    # Assume chat already joined this/other fed
    if "subscribed" in fed and fed_id in fed["subscribed"]:
        await message.reply(
            strings["already_subsed"].format(
                name=html.escape(fed["fed_name"], False),
                name2=html.escape(fed2["fed_name"], False),
            )
        )
        return

    await db.feds.update_one(
        {"_id": fed["_id"]}, {"$addToSet": {"subscribed": {"$each": [fed_id]}}}
    )
    await get_fed_by_id.reset_cache(fed["fed_id"])
    await message.reply(
        strings["subsed_success"].format(
            name=html.escape(fed["fed_name"], False),
            name2=html.escape(fed2["fed_name"], False),
        )
    )


@decorator.register(cmds="funsub")
@need_args_dec()
@get_current_chat_fed
@is_fed_owner
@get_strings_dec("feds")
async def fed_unsub(message, fed, strings):
    fed_id = message.get_args().split(" ")[0]

    if not (fed2 := await get_fed_by_id(fed_id)):
        await message.reply(strings["fed_id_invalid"])
        return

    if "subscribed" in fed and fed_id not in fed["subscribed"]:
        message.reply(
            strings["not_subsed"].format(
                name=html.escape(fed["fed_name"], False), name2=fed2["fed_name"]
            )
        )
        return

    await db.feds.update_one(
        {"_id": fed["_id"]}, {"$pull": {"subscribed": str(fed_id)}}
    )
    await get_fed_by_id.reset_cache(fed["fed_id"])
    await message.reply(
        strings["unsubsed_success"].format(
            name=html.escape(fed["fed_name"], False),
            name2=html.escape(fed2["fed_name"], False),
        )
    )


@decorator.register(cmds="fpromote")
@get_fed_user_text()
@is_fed_owner
@get_strings_dec("feds")
async def promote_to_fed(message, fed, user, text, strings):
    restricted_ids = [1087968824, 777000]
    if user["user_id"] in restricted_ids:
        return await message.reply(strings["restricted_user:promote"])
    await db.feds.update_one(
        {"_id": fed["_id"]}, {"$addToSet": {"admins": {"$each": [user["user_id"]]}}}
    )
    await get_fed_by_id.reset_cache(fed["fed_id"])
    await message.reply(
        strings["admin_added_to_fed"].format(
            user=await get_user_link(user["user_id"]),
            name=html.escape(fed["fed_name"], False),
        )
    )

    await fed_post_log(
        fed,
        strings["promote_user_fed_log"].format(
            fed_name=html.escape(fed["fed_name"], False),
            fed_id=fed["fed_id"],
            user=await get_user_link(user["user_id"]),
            user_id=user["user_id"],
        ),
    )


@decorator.register(cmds="fdemote")
@get_fed_user_text()
@is_fed_owner
@get_strings_dec("feds")
async def demote_from_fed(message, fed, user, text, strings):
    await db.feds.update_one(
        {"_id": fed["_id"]}, {"$pull": {"admins": user["user_id"]}}
    )
    await get_fed_by_id.reset_cache(fed["fed_id"])

    await message.reply(
        strings["admin_demoted_from_fed"].format(
            user=await get_user_link(user["user_id"]),
            name=html.escape(fed["fed_name"], False),
        )
    )

    await fed_post_log(
        fed,
        strings["demote_user_fed_log"].format(
            fed_name=html.escape(fed["fed_name"], False),
            fed_id=fed["fed_id"],
            user=await get_user_link(user["user_id"]),
            user_id=user["user_id"],
        ),
    )


@decorator.register(cmds=["fsetlog", "setfedlog"], only_groups=True)
@get_fed_dec
@get_chat_dec(allow_self=True, fed=True)
@is_fed_owner
@get_strings_dec("feds")
async def set_fed_log_chat(message, fed, chat, strings):
    chat_id = chat["chat_id"] if "chat_id" in chat else chat["id"]
    if chat["type"] == "channel":
        if (
            await check_admin_rights(message, chat_id, BOT_ID, ["can_post_messages"])
            is not True
        ):
            return await message.reply(strings["no_right_to_post"])

    if "log_chat_id" in fed and fed["log_chat_id"]:
        await message.reply(
            strings["already_have_chatlog"].format(
                name=html.escape(fed["fed_name"], False)
            )
        )
        return

    await db.feds.update_one({"_id": fed["_id"]}, {"$set": {"log_chat_id": chat_id}})
    await get_fed_by_id.reset_cache(fed["fed_id"])

    text = strings["set_chat_log"].format(name=html.escape(fed["fed_name"], False))
    await message.reply(text)

    # Current fed variable is not updated
    await fed_post_log(
        await get_fed_by_id(fed["fed_id"]),
        strings["set_log_fed_log"].format(
            fed_name=html.escape(fed["fed_name"], False), fed_id=fed["fed_id"]
        ),
    )


@decorator.register(cmds=["funsetlog", "unsetfedlog"], only_groups=True)
@get_fed_dec
@is_fed_owner
@get_strings_dec("feds")
async def unset_fed_log_chat(message, fed, strings):
    if "log_chat_id" not in fed or not fed["log_chat_id"]:
        await message.reply(
            strings["already_have_chatlog"].format(
                name=html.escape(fed["fed_name"], False)
            )
        )
        return

    await db.feds.update_one({"_id": fed["_id"]}, {"$unset": {"log_chat_id": 1}})
    await get_fed_by_id.reset_cache(fed["fed_id"])

    text = strings["logging_removed"].format(name=html.escape(fed["fed_name"], False))
    await message.reply(text)

    await fed_post_log(
        fed,
        strings["unset_log_fed_log"].format(
            fed_name=html.escape(fed["fed_name"], False), fed_id=fed["fed_id"]
        ),
    )


@decorator.register(cmds=["fchatlist", "fchats"])
@get_fed_dec
@is_fed_admin
@get_strings_dec("feds")
async def fed_chat_list(message, fed, strings):
    text = strings["chats_in_fed"].format(name=html.escape(fed["fed_name"], False))
    if "chats" not in fed:
        return await message.reply(
            strings["no_chats"].format(name=html.escape(fed["fed_name"], False))
        )

    for chat_id in fed["chats"]:
        chat = await db.chat_list.find_one({"chat_id": chat_id})
        text += "* {} (<code>{}</code>)\n".format(chat["chat_title"], chat_id)
    if len(text) > 4096:
        await message.answer_document(
            InputFile(io.StringIO(text), filename="chatlist.txt"),
            strings["too_large"],
            reply=message.message_id,
        )
        return
    await message.reply(text)


@decorator.register(cmds=["fadminlist", "fadmins"])
@get_fed_dec
@is_fed_admin
@get_strings_dec("feds")
async def fed_admins_list(message, fed, strings):
    text = strings["fadmins_header"].format(
        fed_name=html.escape(fed["fed_name"], False)
    )
    text += "* {} (<code>{}</code>)\n".format(
        await get_user_link(fed["creator"]), fed["creator"]
    )
    if "admins" in fed:
        for user_id in fed["admins"]:
            text += "* {} (<code>{}</code>)\n".format(
                await get_user_link(user_id), user_id
            )
    await message.reply(text, disable_notification=True)


@decorator.register(cmds=["finfo", "fedinfo"])
@get_fed_dec
@get_strings_dec("feds")
async def fed_info(message, fed, strings):
    text = strings["finfo_text"]
    banned_num = await db.fed_bans.count_documents({"fed_id": fed["fed_id"]})
    text = text.format(
        name=html.escape(fed["fed_name"], False),
        fed_id=fed["fed_id"],
        creator=await get_user_link(fed["creator"]),
        chats=len(fed["chats"] if "chats" in fed else []),
        fbanned=banned_num,
    )

    if "subscribed" in fed and len(fed["subscribed"]) > 0:
        text += strings["finfo_subs_title"]
        for sfed in fed["subscribed"]:
            sfed = await get_fed_by_id(sfed)
            text += f"* {sfed['fed_name']} (<code>{sfed['fed_id']}</code>)\n"

    await message.reply(text, disable_notification=True)


async def get_all_subs_feds_r(fed_id, new):
    new.append(fed_id)

    fed = await get_fed_by_id(fed_id)
    async for item in db.feds.find({"subscribed": {"$in": [fed["fed_id"]]}}):
        if item["fed_id"] in new:
            continue
        new = await get_all_subs_feds_r(item["fed_id"], new)

    return new


@decorator.register(cmds=["fban", "sfban"])
@get_fed_user_text()
@is_fed_admin
@get_strings_dec("feds")
async def fed_ban_user(message, fed, user, reason, strings):
    user_id = user["user_id"]

    # Checks
    if user_id in OPERATORS:
        await message.reply(strings["user_wl"])
        return

    elif user_id == message.from_user.id:
        await message.reply(strings["fban_self"])
        return

    elif user_id == BOT_ID:
        await message.reply(strings["fban_self"])
        return

    elif user_id == fed["creator"]:
        await message.reply(strings["fban_creator"])
        return

    elif "admins" in fed and user_id in fed["admins"]:
        await message.reply(strings["fban_fed_admin"])
        return

    elif data := await db.fed_bans.find_one(
        {"fed_id": fed["fed_id"], "user_id": user_id}
    ):
        if "reason" not in data or data["reason"] != reason:
            operation = "$set" if reason else "$unset"
            await db.fed_bans.update_one(
                {"_id": data["_id"]}, {operation: {"reason": reason}}
            )
            return await message.reply(strings["update_fban"].format(reason=reason))
        await message.reply(
            strings["already_fbanned"].format(user=await get_user_link(user_id))
        )
        return

    text = strings["fbanned_header"]
    text += strings["fban_info"].format(
        fed=html.escape(fed["fed_name"], False),
        fadmin=await get_user_link(message.from_user.id),
        user=await get_user_link(user_id),
        user_id=user["user_id"],
    )
    if reason:
        text += strings["fbanned_reason"].format(reason=reason)

    # fban processing msg
    num = len(fed["chats"]) if "chats" in fed else 0
    msg = await message.reply(text + strings["fbanned_process"].format(num=num))

    user = await db.user_list.find_one({"user_id": user_id})

    banned_chats = []

    if "chats" in fed:
        for chat_id in fed["chats"]:
            # We not found the user or user wasn't detected
            if not user or "chats" not in user:
                continue

            if chat_id in user["chats"]:
                await asyncio.sleep(0)  # Do not slow down other updates
                if await ban_user(chat_id, user_id):
                    banned_chats.append(chat_id)

    new = {
        "fed_id": fed["fed_id"],
        "user_id": user_id,
        "banned_chats": banned_chats,
        "time": datetime.now(),
        "by": message.from_user.id,
    }

    if reason:
        new["reason"] = reason

    await db.fed_bans.insert_one(new)

    channel_text = strings["fban_log_fed_log"].format(
        fed_name=html.escape(fed["fed_name"], False),
        fed_id=fed["fed_id"],
        user=await get_user_link(user_id),
        user_id=user_id,
        by=await get_user_link(message.from_user.id),
        chat_count=len(banned_chats),
        all_chats=num,
    )

    if reason:
        channel_text += strings["fban_reason_fed_log"].format(reason=reason)

    # Check if silent
    silent = False
    if get_cmd(message) == "sfban":
        silent = True
        key = "leave_silent:" + str(message.chat.id)
        redis.set(key, user_id)
        redis.expire(key, 30)
        text += strings["fbanned_silence"]

    # SubsFeds process
    if len(sfeds_list := await get_all_subs_feds_r(fed["fed_id"], [])) > 1:
        sfeds_list.remove(fed["fed_id"])
        this_fed_banned_count = len(banned_chats)

        await msg.edit_text(
            text + strings["fbanned_subs_process"].format(feds=len(sfeds_list))
        )

        all_banned_chats_count = 0
        for s_fed_id in sfeds_list:
            if (
                await db.fed_bans.find_one({"fed_id": s_fed_id, "user_id": user_id})
                is not None
            ):
                # user is already banned in subscribed federation, skip
                continue
            s_fed = await get_fed_by_id(s_fed_id)
            banned_chats = []
            new = {
                "fed_id": s_fed_id,
                "user_id": user_id,
                "banned_chats": banned_chats,
                "time": datetime.now(),
                "origin_fed": fed["fed_id"],
                "by": message.from_user.id,
            }
            for chat_id in s_fed["chats"]:
                if not user:
                    continue

                elif chat_id == user["user_id"]:
                    continue

                elif "chats" not in user:
                    continue

                elif chat_id not in user["chats"]:
                    continue

                # Do not slow down other updates
                await asyncio.sleep(0.2)

                if await ban_user(chat_id, user_id):
                    banned_chats.append(chat_id)
                    all_banned_chats_count += 1

                    if reason:
                        new["reason"] = reason

            await db.fed_bans.insert_one(new)

        await msg.edit_text(
            text
            + strings["fbanned_subs_done"].format(
                chats=this_fed_banned_count,
                subs_chats=all_banned_chats_count,
                feds=len(sfeds_list),
            )
        )

        channel_text += strings["fban_subs_fed_log"].format(
            subs_chats=all_banned_chats_count, feds=len(sfeds_list)
        )

    else:
        await msg.edit_text(
            text + strings["fbanned_done"].format(num=len(banned_chats))
        )

    await fed_post_log(fed, channel_text)

    if silent:
        to_del = [msg.message_id, message.message_id]
        if (
            "reply_to_message" in message
            and message.reply_to_message.from_user.id == user_id
        ):
            to_del.append(message.reply_to_message.message_id)
        await asyncio.sleep(5)
        await tbot.delete_messages(message.chat.id, to_del)


@decorator.register(cmds=["unfban", "funban"])
@get_fed_user_text()
@is_fed_admin
@get_strings_dec("feds")
async def unfed_ban_user(message, fed, user, text, strings):
    user_id = user["user_id"]

    if user == BOT_ID:
        await message.reply(strings["unfban_self"])
        return

    elif not (
        banned := await db.fed_bans.find_one(
            {"fed_id": fed["fed_id"], "user_id": user_id}
        )
    ):
        await message.reply(
            strings["user_not_fbanned"].format(user=await get_user_link(user_id))
        )
        return

    text = strings["un_fbanned_header"]
    text += strings["fban_info"].format(
        fed=html.escape(fed["fed_name"], False),
        fadmin=await get_user_link(message.from_user.id),
        user=await get_user_link(user["user_id"]),
        user_id=user["user_id"],
    )

    banned_chats = []
    if "banned_chats" in banned:
        banned_chats = banned["banned_chats"]

    # unfban processing msg
    msg = await message.reply(
        text + strings["un_fbanned_process"].format(num=len(banned_chats))
    )

    counter = 0
    for chat_id in banned_chats:
        await asyncio.sleep(0)  # Do not slow down other updates
        if await unban_user(chat_id, user_id):
            counter += 1

    await db.fed_bans.delete_one({"fed_id": fed["fed_id"], "user_id": user_id})

    channel_text = strings["un_fban_log_fed_log"].format(
        fed_name=html.escape(fed["fed_name"], False),
        fed_id=fed["fed_id"],
        user=await get_user_link(user["user_id"]),
        user_id=user["user_id"],
        by=await get_user_link(message.from_user.id),
        chat_count=len(banned_chats),
        all_chats=len(fed["chats"]) if "chats" in fed else 0,
    )

    # Subs feds
    if len(sfeds_list := await get_all_subs_feds_r(fed["fed_id"], [])) > 1:
        sfeds_list.remove(fed["fed_id"])
        this_fed_unbanned_count = counter

        await msg.edit_text(
            text + strings["un_fbanned_subs_process"].format(feds=len(sfeds_list))
        )

        all_unbanned_chats_count = 0
        for sfed_id in sfeds_list:
            # revision 19/10/2020: unfbans only those who got banned by `this` fed
            ban = await db.fed_bans.find_one(
                {"fed_id": sfed_id, "origin_fed": fed["fed_id"], "user_id": user_id}
            )
            if ban is None:
                # probably old fban
                ban = await db.fed_bans.find_one(
                    {"fed_id": sfed_id, "user_id": user_id}
                )
                # if ban['time'] > `replace here with datetime of release of v2.2`:
                #    continue
            banned_chats = []
            if ban is not None and "banned_chats" in ban:
                banned_chats = ban["banned_chats"]

            for chat_id in banned_chats:
                await asyncio.sleep(0.2)  # Do not slow down other updates
                if await unban_user(chat_id, user_id):
                    all_unbanned_chats_count += 1

                    await db.fed_bans.delete_one(
                        {"fed_id": sfed_id, "user_id": user_id}
                    )

        await msg.edit_text(
            text
            + strings["un_fbanned_subs_done"].format(
                chats=this_fed_unbanned_count,
                subs_chats=all_unbanned_chats_count,
                feds=len(sfeds_list),
            )
        )

        channel_text += strings["fban_subs_fed_log"].format(
            subs_chats=all_unbanned_chats_count, feds=len(sfeds_list)
        )
    else:
        await msg.edit_text(text + strings["un_fbanned_done"].format(num=counter))

    await fed_post_log(fed, channel_text)


@decorator.register(cmds=["delfed", "fdel"])
@get_fed_dec
@is_fed_owner
@get_strings_dec("feds")
async def del_fed_cmd(message, fed, strings):
    fed_name = html.escape(fed["fed_name"], False)
    fed_id = fed["fed_id"]
    fed_owner = fed["creator"]

    buttons = InlineKeyboardMarkup()
    buttons.add(
        InlineKeyboardButton(
            text=strings["delfed_btn_yes"],
            callback_data=delfed_cb.new(fed_id=fed_id, creator_id=fed_owner),
        )
    )
    buttons.add(
        InlineKeyboardButton(
            text=strings["delfed_btn_no"], callback_data=f"cancel_{fed_owner}"
        )
    )

    await message.reply(strings["delfed"] % fed_name, reply_markup=buttons)


@decorator.register(delfed_cb.filter(), f="cb", allow_kwargs=True)
@get_strings_dec("feds")
async def del_fed_func(event, strings, callback_data=None, **kwargs):
    fed_id = callback_data["fed_id"]
    fed_owner = callback_data["creator_id"]

    if event.from_user.id != int(fed_owner):
        return

    await db.feds.delete_one({"fed_id": fed_id})
    await get_fed_by_id.reset_cache(fed_id)
    await get_fed_by_creator.reset_cache(int(fed_owner))
    async for subscribed_fed in db.feds.find({"subscribed": fed_id}):
        await db.feds.update_one(
            {"_id": subscribed_fed["_id"]}, {"$pull": {"subscribed": fed_id}}
        )
        await get_fed_by_id.reset_cache(subscribed_fed["fed_id"])

    # delete all fbans of it
    await db.fed_bans.delete_many({"fed_id": fed_id})

    await event.message.edit_text(strings["delfed_success"])


@decorator.register(regexp="cancel_(.*)", f="cb")
async def cancel(event):
    if event.from_user.id != int((re.search(r"cancel_(.*)", event.data)).group(1)):
        return
    await event.message.delete()


@decorator.register(cmds="frename")
@need_args_dec()
@get_fed_dec
@is_fed_owner
@get_strings_dec("feds")
async def fed_rename(message, fed, strings):
    # Check whether first arg is fed ID | TODO: Remove this
    args = message.get_args().split(" ", 2)
    if len(args) > 1 and args[0].count("-") == 4:
        new_name = " ".join(args[1:])
    else:
        new_name = " ".join(args[0:])

    if new_name == fed["fed_name"]:
        await message.reply(strings["frename_same_name"])
        return

    await db.feds.update_one({"_id": fed["_id"]}, {"$set": {"fed_name": new_name}})
    await get_fed_by_id.reset_cache(fed["fed_id"])
    await message.reply(
        strings["frename_success"].format(
            old_name=html.escape(fed["fed_name"], False),
            new_name=html.escape(new_name, False),
        )
    )


@decorator.register(cmds=["fbanlist", "exportfbans", "fexport"])
@get_fed_dec
@is_fed_admin
@get_strings_dec("feds")
async def fban_export(message, fed, strings):
    fed_id = fed["fed_id"]
    key = "fbanlist_lock:" + str(fed_id)
    if redis.get(key) and message.from_user.id not in OPERATORS:
        ttl = format_timedelta(
            timedelta(seconds=redis.ttl(key)), strings["language_info"]["babel"]
        )
        await message.reply(strings["fbanlist_locked"] % ttl)
        return

    redis.set(key, 1)
    redis.expire(key, 600)

    msg = await message.reply(strings["creating_fbanlist"])
    fields = ["user_id", "reason", "by", "time", "banned_chats"]
    with io.StringIO() as f:
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        async for banned_data in db.fed_bans.find({"fed_id": fed_id}):
            await asyncio.sleep(0)

            data = {"user_id": banned_data["user_id"]}

            if "reason" in banned_data:
                data["reason"] = banned_data["reason"]

            if "time" in banned_data:
                data["time"] = int(time.mktime(banned_data["time"].timetuple()))

            if "by" in banned_data:
                data["by"] = banned_data["by"]

            if "banned_chats" in banned_data:
                data["banned_chats"] = banned_data["banned_chats"]

            writer.writerow(data)

        text = strings["fbanlist_done"] % html.escape(fed["fed_name"], False)
        f.seek(0)
        await message.answer_document(InputFile(f, filename="fban_export.csv"), text)
    await msg.delete()


@decorator.register(cmds=["importfbans", "fimport"])
@get_fed_dec
@is_fed_admin
@get_strings_dec("feds")
async def importfbans_cmd(message, fed, strings):
    fed_id = fed["fed_id"]
    key = "importfbans_lock:" + str(fed_id)
    if redis.get(key) and message.from_user.id not in OPERATORS:
        ttl = format_timedelta(
            timedelta(seconds=redis.ttl(key)), strings["language_info"]["babel"]
        )
        await message.reply(strings["importfbans_locked"] % ttl)
        return

    redis.set(key, 1)
    redis.expire(key, 600)

    if "document" in message:
        document = message.document
    else:
        if "reply_to_message" not in message:
            await ImportFbansFileWait.waiting.set()
            await message.reply(strings["send_import_file"])
            return

        elif "document" not in message.reply_to_message:
            await message.reply(strings["rpl_to_file"])
            return
        document = message.reply_to_message.document

    await importfbans_func(message, fed, document=document)


@get_strings_dec("feds")
async def importfbans_func(message, fed, strings, document=None):
    global user_id
    file_type = os.path.splitext(document["file_name"])[1][1:]

    if file_type == "json":
        if document["file_size"] > 1000000:
            await message.reply(strings["big_file_json"].format(num="1"))
            return
    elif file_type == "csv":
        if document["file_size"] > 52428800:
            await message.reply(strings["big_file_csv"].format(num="50"))
            return
    else:
        await message.reply(strings["wrong_file_ext"])
        return

    f = await bot.download_file_by_id(document.file_id, io.BytesIO())
    msg = await message.reply(strings["importing_process"])

    data = None
    if file_type == "json":
        try:
            data = rapidjson.load(f).items()
        except ValueError:
            return await message.reply(strings["invalid_file"])
    elif file_type == "csv":
        data = csv.DictReader(io.TextIOWrapper(f))

    real_counter = 0

    queue_del = []
    queue_insert = []
    current_time = datetime.now()
    for row in data:
        if file_type == "json":
            user_id = row[0]
            data = row[1]
        elif file_type == "csv":
            if "user_id" in row:
                user_id = int(row["user_id"])
            elif "id" in row:
                user_id = int(row["id"])
            else:
                continue
        else:
            raise NotImplementedError

        new = {"fed_id": fed["fed_id"], "user_id": user_id}

        if "reason" in row:
            new["reason"] = row["reason"]

        if "by" in row:
            new["by"] = int(row["by"])
        else:
            new["by"] = message.from_user.id

        if "time" in row:
            new["time"] = datetime.fromtimestamp(int(row["time"]))
        else:
            new["time"] = current_time

        if "banned_chats" in row and type(row["banned_chats"]) is list:
            new["banned_chats"] = row["banned_chats"]

        queue_del.append(DeleteMany({"fed_id": fed["fed_id"], "user_id": user_id}))
        queue_insert.append(InsertOne(new))

        if len(queue_insert) == 1000:
            real_counter += len(queue_insert)

            # Make delete operation ordered before inserting.
            if queue_del:
                await db.fed_bans.bulk_write(queue_del, ordered=False)
            await db.fed_bans.bulk_write(queue_insert, ordered=False)

            queue_del = []
            queue_insert = []

    # Process last bans
    real_counter += len(queue_insert)
    if queue_del:
        await db.fed_bans.bulk_write(queue_del, ordered=False)
    if queue_insert:
        await db.fed_bans.bulk_write(queue_insert, ordered=False)

    await msg.edit_text(strings["import_done"].format(num=real_counter))


@decorator.register(
    state=ImportFbansFileWait.waiting,
    content_types=types.ContentTypes.DOCUMENT,
    allow_kwargs=True,
)
@get_fed_dec
@is_fed_admin
async def import_state(message, fed, state=None, **kwargs):
    await importfbans_func(message, fed, document=message.document)
    await state.finish()


@decorator.register(only_groups=True)
@chat_connection(only_groups=True)
@get_strings_dec("feds")
async def check_fbanned(message: Message, chat, strings):
    if message.sender_chat:
        # should be channel/anon
        return

    user_id = message.from_user.id
    chat_id = chat["chat_id"]

    if not (fed := await get_fed_f(message)):
        return

    elif await is_user_admin(chat_id, user_id):
        return

    feds_list = [fed["fed_id"]]

    if "subscribed" in fed:
        feds_list.extend(fed["subscribed"])

    if ban := await db.fed_bans.find_one(
        {"fed_id": {"$in": feds_list}, "user_id": user_id}
    ):

        # check whether banned fed_id is chat's fed id else
        # user is banned in sub fed
        if fed["fed_id"] == ban["fed_id"] and "origin_fed" not in ban:
            text = strings["automatic_ban"].format(
                user=await get_user_link(user_id),
                fed_name=html.escape(fed["fed_name"], False),
            )
        else:
            s_fed = await get_fed_by_id(
                ban["fed_id"] if "origin_fed" not in ban else ban["origin_fed"]
            )
            if s_fed is None:
                return

            text = strings["automatic_ban_sfed"].format(
                user=await get_user_link(user_id), fed_name=s_fed["fed_name"]
            )

        if "reason" in ban:
            text += strings["automatic_ban_reason"].format(text=ban["reason"])

        if not await ban_user(chat_id, user_id):
            return

        await message.reply(text)

        await db.fed_bans.update_one(
            {"_id": ban["_id"]}, {"$addToSet": {"banned_chats": chat_id}}
        )


@decorator.register(cmds=["fcheck", "fbanstat"])
@get_fed_user_text(skip_no_fed=True, self=True)
@get_strings_dec("feds")
async def fedban_check(message, fed, user, _, strings):
    fbanned_fed = False  # A variable to find if user is banned in current fed of chat
    fban_data = None

    total_count = await db.fed_bans.count_documents({"user_id": user["user_id"]})
    if fed:
        fed_list = [fed["fed_id"]]
        # check fbanned in subscribed
        if "subscribed" in fed:
            fed_list.extend(fed["subscribed"])

        if fban_data := await db.fed_bans.find_one(
            {"user_id": user["user_id"], "fed_id": {"$in": fed_list}}
        ):
            fbanned_fed = True

            # re-assign fed if user is banned in sub-fed
            if fban_data["fed_id"] != fed["fed_id"] or "origin_fed" in fban_data:
                fed = await get_fed_by_id(
                    fban_data[
                        "fed_id" if "origin_fed" not in fban_data else "origin_fed"
                    ]
                )

    # create text
    text = strings["fcheck_header"]
    if message.chat.type == "private" and message.from_user.id == user["user_id"]:
        if bool(fed):
            if bool(fban_data):
                if "reason" not in fban_data:
                    text += strings["fban_info:fcheck"].format(
                        fed=html.escape(fed["fed_name"], False),
                        date=babel.dates.format_date(
                            fban_data["time"],
                            "long",
                            locale=strings["language_info"]["babel"],
                        ),
                    )
                else:
                    text += strings["fban_info:fcheck:reason"].format(
                        fed=html.escape(fed["fed_name"], False),
                        date=babel.dates.format_date(
                            fban_data["time"],
                            "long",
                            locale=strings["language_info"]["babel"],
                        ),
                        reason=fban_data["reason"],
                    )
            else:
                return await message.reply(strings["didnt_fbanned"])
        else:
            text += strings["fbanned_count_pm"].format(count=total_count)
            if total_count > 0:
                count = 0
                async for fban in db.fed_bans.find({"user_id": user["user_id"]}):
                    count += 1
                    _fed = await get_fed_by_id(fban["fed_id"])
                    if _fed:
                        fed_name = _fed["fed_name"]
                        text += f'{count}: <code>{fban["fed_id"]}</code>: {fed_name}\n'
    else:
        if total_count > 0:
            text += strings["fbanned_data"].format(
                user=await get_user_link(user["user_id"]), count=total_count
            )
        else:
            text += strings["fbanned_nowhere"].format(
                user=await get_user_link(user["user_id"])
            )

        if fbanned_fed is True:
            if "reason" in fban_data:
                text += strings["fbanned_in_fed:reason"].format(
                    fed=html.escape(fed["fed_name"], False), reason=fban_data["reason"]
                )
            else:
                text += strings["fbanned_in_fed"].format(
                    fed=html.escape(fed["fed_name"], False)
                )
        elif fed is not None:
            text += strings["not_fbanned_in_fed"].format(
                fed_name=html.escape(fed["fed_name"], quote=False)
            )

        if total_count > 0:
            if message.from_user.id == user["user_id"]:
                text += strings["contact_in_pm"]
    if len(text) > 4096:
        return await message.answer_document(
            InputFile(io.StringIO(text), filename="fban_info.txt"),
            strings["too_long_fbaninfo"],
            reply=message.message_id,
        )
    await message.reply(text)


@cached()
async def get_fed_by_id(fed_id: str) -> Optional[dict]:
    return await db.feds.find_one({"fed_id": fed_id})


@cached()
async def get_fed_by_creator(creator: int) -> Optional[dict]:
    return await db.feds.find_one({"creator": creator})


async def __export__(chat_id):
    if chat_fed := await db.feds.find_one({"chats": [chat_id]}):
        return {"feds": {"fed_id": chat_fed["fed_id"]}}


async def __import__(chat_id, data):
    if fed_id := data["fed_id"]:
        if current_fed := await db.feds.find_one({"chats": [int(chat_id)]}):
            await db.feds.update_one(
                {"_id": current_fed["_id"]}, {"$pull": {"chats": chat_id}}
            )
            await get_fed_by_id.reset_cache(current_fed["fed_id"])
        await db.feds.update_one({"fed_id": fed_id}, {"$addToSet": {"chats": chat_id}})
        await get_fed_by_id.reset_cache(fed_id)


__mod_name__ = "Federations"

__help__ = """
Well basically there is 2 reasons to use Federations:
1. You have many chats and want to ban users in all of them with 1 command
2. You want to subscribe to any of the antispam Federations to have your chat(s) protected.
In both cases Daisy will help you.
<b>Arguments types help:</b>
<code>()</code>: required argument
<code>(user)</code>: required but you can reply on any user's message instead
<code>(file)</code>: required file, if file isn't provided you will be entered in file state, this means Daisy will wait file message from you. Type /cancel to leave from it.
<code>(? )</code>: additional argument
<b>Only Federation owner:</b>
- /fnew (name) or /newfed (name): Creates a new Federation
- /frename (?Fed ID) (new name): Renames your federation
- /fdel (?Fed ID) or /delfed (?Fed ID): Removes your Federation
- /fpromote (user) (?Fed ID): Promotes a user to the your Federation
- /fdemote (user) (?Fed ID): Demotes a user from the your Federation
- /fsub (Fed ID): Subscibes your Federation over provided
- /funsub (Fed ID): unsubscibes your Federation from provided
- /fsetlog (? Fed ID) (? chat/channel id) or /setfedlog (? Fed ID) (? chat/channel id): Set's a log chat/channel for your Federation
- /funsetlog (?Fed ID) or /unsetfedlog (?Fed ID): Unsets a Federation log chat\channel
- /fexport (?Fed ID): Exports Federation bans
- /fimport (?Fed ID) (file): Imports Federation bans
<b>Only Chat owner:</b>
- /fjoin (Fed ID) or /joinfed (Fed ID): Joins current chat to provided Federation
- /fleave or /leavefed: Leaves current chat from the fed
<b>Avaible for Federation admins and owners:</b>
- /fchatlist (?Fed ID) or /fchats (?Fed ID): Shows a list of chats in the your Federation list
- /fban (user) (?Fed ID) (?reason): Bans user in the Fed and Feds which subscribed on this Fed
- /sfban (user) (?Fed ID) (?reason): As above, but silently - means the messages about fbanning and replied message (if was provided) will be removed
- /unfban (user) (?Fed ID) (?reason): Unbans a user from a Federation
<b>Avaible for all users:</b>
- /fcheck (?user): Check user's federation ban info
- /finfo (?Fed ID): Info about Federation
"""
