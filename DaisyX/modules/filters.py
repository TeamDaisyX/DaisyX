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
import functools
import random
import re
from contextlib import suppress
from string import printable

import regex
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageCantBeDeleted, MessageToDeleteNotFound
from async_timeout import timeout
from bson.objectid import ObjectId
from pymongo import UpdateOne

from DaisyX import bot, loop
from DaisyX.decorator import register
from DaisyX.modules import LOADED_MODULES
from DaisyX.services.mongo import db
from DaisyX.services.redis import redis
from DaisyX.utils.logger import log

from .utils.connections import chat_connection, get_connected_chat
from .utils.language import get_string, get_strings_dec
from .utils.message import get_args_str, need_args_dec
from .utils.user_details import is_chat_creator, is_user_admin

filter_action_cp = CallbackData("filter_action_cp", "filter_id")
filter_remove_cp = CallbackData("filter_remove_cp", "id")
filter_delall_yes_cb = CallbackData("filter_delall_yes_cb", "chat_id")

FILTERS_ACTIONS = {}


class NewFilter(StatesGroup):
    handler = State()
    setup = State()


async def update_handlers_cache(chat_id):
    redis.delete(f"filters_cache_{chat_id}")
    filters = db.filters.find({"chat_id": chat_id})
    handlers = []
    async for filter in filters:
        handler = filter["handler"]
        if handler in handlers:
            continue

        handlers.append(handler)
        redis.lpush(f"filters_cache_{chat_id}", handler)

    return handlers


@register()
async def check_msg(message):
    log.debug("Running check msg for filters function.")
    chat = await get_connected_chat(message, only_groups=True)
    if "err_msg" in chat or message.chat.type == "private":
        return

    chat_id = chat["chat_id"]
    if not (filters := redis.lrange(f"filters_cache_{chat_id}", 0, -1)):
        filters = await update_handlers_cache(chat_id)

    if len(filters) == 0:
        return

    text = message.text

    # Workaround to disable all filters if admin want to remove filter
    if await is_user_admin(chat_id, message.from_user.id):
        if text[1:].startswith("addfilter") or text[1:].startswith("delfilter"):
            return

    for handler in filters:  # type: str
        if handler.startswith("re:"):
            func = functools.partial(
                regex.search, handler.replace("re:", "", 1), text, timeout=0.1
            )
        else:
            # TODO: Remove this (handler.replace(...)). kept for backward compatibility
            func = functools.partial(
                re.search,
                re.escape(handler).replace("(+)", "(.*)"),
                text,
                flags=re.IGNORECASE,
            )

        try:
            async with timeout(0.1):
                matched = await loop.run_in_executor(None, func)
        except (asyncio.TimeoutError, TimeoutError):
            continue

        if matched:
            # We can have few filters with same handler, that's why we create a new loop.
            filters = db.filters.find({"chat_id": chat_id, "handler": handler})
            async for filter in filters:
                action = filter["action"]
                await FILTERS_ACTIONS[action]["handle"](message, chat, filter)


@register(cmds=["addfilter", "newfilter"], is_admin=True, user_can_change_info=True)
@need_args_dec()
@chat_connection(only_groups=True, admin=True)
@get_strings_dec("filters")
async def add_handler(message, chat, strings):
    # filters doesn't support anon admins
    if message.from_user.id == 1087968824:
        return await message.reply(strings["anon_detected"])
    # if not await check_admin_rights(message, chat_id, message.from_user.id, ["can_change_info"]):
    # return await message.reply("You can't change info of this group")

    handler = get_args_str(message)

    if handler.startswith("re:"):
        pattern = handler
        random_text_str = "".join(random.choice(printable) for i in range(50))
        try:
            regex.match(pattern, random_text_str, timeout=0.2)
        except TimeoutError:
            await message.reply(strings["regex_too_slow"])
            return
    else:
        handler = handler.lower()

    text = strings["adding_filter"].format(
        handler=handler, chat_name=chat["chat_title"]
    )

    buttons = InlineKeyboardMarkup(row_width=2)
    for action in FILTERS_ACTIONS.items():
        filter_id = action[0]
        data = action[1]

        buttons.insert(
            InlineKeyboardButton(
                await get_string(
                    chat["chat_id"], data["title"]["module"], data["title"]["string"]
                ),
                callback_data=filter_action_cp.new(filter_id=filter_id),
            )
        )
    buttons.add(InlineKeyboardButton(strings["cancel_btn"], callback_data="cancel"))

    user_id = message.from_user.id
    chat_id = chat["chat_id"]
    redis.set(f"add_filter:{user_id}:{chat_id}", handler)
    if handler is not None:
        await message.reply(text, reply_markup=buttons)


async def save_filter(message, data, strings):
    if await db.filters.find_one(data):
        # prevent saving duplicate filter
        await message.reply("Duplicate filter!")
        return

    await db.filters.insert_one(data)
    await update_handlers_cache(data["chat_id"])
    await message.reply(strings["saved"])


@register(filter_action_cp.filter(), f="cb", allow_kwargs=True)
@chat_connection(only_groups=True, admin=True)
@get_strings_dec("filters")
async def register_action(
    event, chat, strings, callback_data=None, state=None, **kwargs
):
    if not await is_user_admin(event.message.chat.id, event.from_user.id):
        return await event.answer("You are not admin to do this")
    filter_id = callback_data["filter_id"]
    action = FILTERS_ACTIONS[filter_id]

    user_id = event.from_user.id
    chat_id = chat["chat_id"]

    handler = redis.get(f"add_filter:{user_id}:{chat_id}")

    if not handler:
        return await event.answer(
            "Something went wrong! Please try again!", show_alert=True
        )

    data = {"chat_id": chat_id, "handler": handler, "action": filter_id}

    if "setup" in action:
        await NewFilter.setup.set()
        setup_co = len(action["setup"]) - 1 if type(action["setup"]) is list else 0
        async with state.proxy() as proxy:
            proxy["data"] = data
            proxy["filter_id"] = filter_id
            proxy["setup_co"] = setup_co
            proxy["setup_done"] = 0
            proxy["msg_id"] = event.message.message_id

        if setup_co > 0:
            await action["setup"][0]["start"](event.message)
        else:
            await action["setup"]["start"](event.message)
        return

    await save_filter(event.message, data, strings)


@register(state=NewFilter.setup, f="any", is_admin=True, allow_kwargs=True)
@chat_connection(only_groups=True, admin=True)
@get_strings_dec("filters")
async def setup_end(message, chat, strings, state=None, **kwargs):
    async with state.proxy() as proxy:
        data = proxy["data"]
        filter_id = proxy["filter_id"]
        setup_co = proxy["setup_co"]
        curr_step = proxy["setup_done"]
        with suppress(MessageCantBeDeleted, MessageToDeleteNotFound):
            await bot.delete_message(message.chat.id, proxy["msg_id"])

    action = FILTERS_ACTIONS[filter_id]

    func = (
        action["setup"][curr_step]["finish"]
        if type(action["setup"]) is list
        else action["setup"]["finish"]
    )
    if not bool(a := await func(message, data)):
        await state.finish()
        return

    data.update(a)

    if setup_co > 0:
        await action["setup"][curr_step + 1]["start"](message)
        async with state.proxy() as proxy:
            proxy["data"] = data
            proxy["setup_co"] -= 1
            proxy["setup_done"] += 1
        return

    await state.finish()
    await save_filter(message, data, strings)


@register(cmds=["filters", "listfilters"])
@chat_connection(only_groups=True)
@get_strings_dec("filters")
async def list_filters(message, chat, strings):
    text = strings["list_filters"].format(chat_name=chat["chat_title"])

    filters = db.filters.find({"chat_id": chat["chat_id"]})
    filters_text = ""
    async for filter in filters:
        filters_text += f"- {filter['handler']}: {filter['action']}\n"

    if not filters_text:
        await message.reply(
            strings["no_filters_found"].format(chat_name=chat["chat_title"])
        )
        return

    await message.reply(text + filters_text)


@register(cmds="delfilter", is_admin=True, user_can_change_info=True)
@need_args_dec()
@chat_connection(only_groups=True, admin=True)
@get_strings_dec("filters")
async def del_filter(message, chat, strings):
    handler = get_args_str(message)
    chat_id = chat["chat_id"]
    filters = await db.filters.find({"chat_id": chat_id, "handler": handler}).to_list(
        9999
    )
    if not filters:
        await message.reply(
            strings["no_such_filter"].format(chat_name=chat["chat_title"])
        )
        return

    # Remove filter in case if we found only 1 filter with same header
    filter = filters[0]
    if len(filters) == 1:
        await db.filters.delete_one({"_id": filter["_id"]})
        await update_handlers_cache(chat_id)
        await message.reply(strings["del_filter"].format(handler=filter["handler"]))
        return

    # Build keyboard row for select which exactly filter user want to remove
    buttons = InlineKeyboardMarkup(row_width=1)
    text = strings["select_filter_to_remove"].format(handler=handler)
    for filter in filters:
        action = FILTERS_ACTIONS[filter["action"]]
        buttons.add(
            InlineKeyboardButton(
                # If module's filter support custom del btn names else just show action name
                "" + action["del_btn_name"](message, filter)
                if "del_btn_name" in action
                else filter["action"],
                callback_data=filter_remove_cp.new(id=str(filter["_id"])),
            )
        )

    await message.reply(text, reply_markup=buttons)


@register(filter_remove_cp.filter(), f="cb", allow_kwargs=True)
@chat_connection(only_groups=True, admin=True)
@get_strings_dec("filters")
async def del_filter_cb(event, chat, strings, callback_data=None, **kwargs):
    if not await is_user_admin(event.message.chat.id, event.from_user.id):
        return await event.answer("You are not admin to do this")
    filter_id = ObjectId(callback_data["id"])
    filter = await db.filters.find_one({"_id": filter_id})
    await db.filters.delete_one({"_id": filter_id})
    await update_handlers_cache(chat["chat_id"])
    await event.message.edit_text(
        strings["del_filter"].format(handler=filter["handler"])
    )
    return


@register(cmds=["delfilters", "delallfilters"])
@get_strings_dec("filters")
async def delall_filters(message: Message, strings: dict):
    if not await is_chat_creator(message, message.chat.id, message.from_user.id):
        return await message.reply(strings["not_chat_creator"])
    buttons = InlineKeyboardMarkup()
    buttons.add(
        *[
            InlineKeyboardButton(
                strings["confirm_yes"],
                callback_data=filter_delall_yes_cb.new(chat_id=message.chat.id),
            ),
            InlineKeyboardButton(
                strings["confirm_no"], callback_data="filter_delall_no_cb"
            ),
        ]
    )
    return await message.reply(strings["delall_header"], reply_markup=buttons)


@register(filter_delall_yes_cb.filter(), f="cb", allow_kwargs=True)
@get_strings_dec("filters")
async def delall_filters_yes(
    event: CallbackQuery, strings: dict, callback_data: dict, **_
):
    if not await is_chat_creator(
        event, chat_id := int(callback_data["chat_id"]), event.from_user.id
    ):
        return False
    result = await db.filters.delete_many({"chat_id": chat_id})
    await update_handlers_cache(chat_id)
    return await event.message.edit_text(
        strings["delall_success"].format(count=result.deleted_count)
    )


@register(regexp="filter_delall_no_cb", f="cb")
@get_strings_dec("filters")
async def delall_filters_no(event: CallbackQuery, strings: dict):
    if not await is_chat_creator(event, event.message.chat.id, event.from_user.id):
        return False
    await event.message.delete()


async def __before_serving__(loop):
    log.debug("Adding filters actions")
    for module in LOADED_MODULES:
        if not getattr(module, "__filters__", None):
            continue

        module_name = module.__name__.split(".")[-1]
        log.debug(f"Adding filter action from {module_name} module")
        for data in module.__filters__.items():
            FILTERS_ACTIONS[data[0]] = data[1]


async def __export__(chat_id):
    data = []
    filters = db.filters.find({"chat_id": chat_id})
    async for filter in filters:
        del filter["_id"], filter["chat_id"]
        if "time" in filter:
            filter["time"] = str(filter["time"])
        data.append(filter)

    return {"filters": data}


async def __import__(chat_id, data):
    new = []
    for filter in data:
        new.append(
            UpdateOne(
                {
                    "chat_id": chat_id,
                    "handler": filter["handler"],
                    "action": filter["action"],
                },
                {"$set": filter},
                upsert=True,
            )
        )
    await db.filters.bulk_write(new)
    await update_handlers_cache(chat_id)


__mod_name__ = "Filters"

__help__ = """
<b> GENERAL FILTERS </b>
Filter module is great for everything! filter in here is used to filter words or sentences in your chat - send notes, warn, ban those!
<i> General (Admins):</i>
- /addfilter (word/sentence): This is used to add filters.
- /delfilter (word/sentence): Use this command to remove a specific filter.
- /delallfilters: As in command this is used to remove all filters of group.

<i> As of now, there is 6 actions that you can do: </i>
- <code>Send a note</code>
- <code>Warn the user</code>
- <code>Ban the user</code>
- <code>Mute the user</code>
- <code>tBan the user</code>
- <code>tMute the user</code>

<i> A filter can support multiple actions ! </i>

Ah if you don't understand what this actions are for? Actions says bot what to do when the given <code>word/sentence</code> is triggered.
You can also use regex and buttons for filters. Check /buttonshelp to know more.

<i> Available for all users:</i>
- /filters or /listfilters

You want to know all filter of your chat/ chat you joined? Use this command. It will list all filters along with specified actions !

<b> TEXT FILTERS </b>
Text filters are for short and text replies
<i> Commands available </i>
- /filter [KEYWORD] [REPLY TO MESSAGE] : Filters the replied message with given keyword.
- /stop [KEYWORD] : Stops the given filter.


<i> Difference between text filter and filter</i>
* If you filtered word "hi" with /addfilter it filters all words including hi. 
  Future explained:
    - When a filter added to hi as "hello" when user sent a message like "It was a hit" bot replies as "Hello" as word contain hi
    ** You can use regex to remove this if you like
<i> Text filters won't reply like that. It only replies if word = "hi" (According to example taken) </i>
Text filters can filter
- <code>A single word</code>
- <code>A sentence</code>
- <code>A sticker</code>

<b> CLASSIC FILTERS </b>
Classic filters are just like marie's filter system. If you still like that kind of filter system. Use /cfilterhelp to know more

⚠️ READ FROM TOP
"""
