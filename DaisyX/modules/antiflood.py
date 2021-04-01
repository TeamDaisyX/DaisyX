# This file is part of Daisy (Telegram Bot)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the`
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pickle
from dataclasses import dataclass
from typing import Optional

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import ChatType, InlineKeyboardMarkup
from aiogram.types.callback_query import CallbackQuery
from aiogram.types.inline_keyboard import InlineKeyboardButton
from aiogram.types.message import ContentType, Message
from aiogram.utils.callback_data import CallbackData
from babel.dates import format_timedelta

from DaisyX import dp
from DaisyX.decorator import register
from DaisyX.modules.utils.connections import chat_connection
from DaisyX.modules.utils.language import get_strings, get_strings_dec
from DaisyX.modules.utils.message import convert_time, get_args, need_args_dec
from DaisyX.modules.utils.restrictions import ban_user, kick_user, mute_user
from DaisyX.modules.utils.user_details import get_user_link, is_user_admin
from DaisyX.services.mongo import db
from DaisyX.services.redis import bredis, redis
from DaisyX.utils.cached import cached
from DaisyX.utils.logger import log

cancel_state = CallbackData("cancel_state", "user_id")


class AntiFloodConfigState(StatesGroup):
    expiration_proc = State()


@dataclass
class CacheModel:
    count: int


class AntifloodEnforcer(BaseMiddleware):
    state_cache_key = "floodstate:{chat_id}"

    async def enforcer(self, message: Message, database: dict):
        if (not (data := self.get_flood(message))) or int(
            self.get_state(message)
        ) != message.from_user.id:
            to_set = CacheModel(count=1)
            self.insert_flood(to_set, message, database)
            self.set_state(message)
            return False  # we aint banning anybody

        # update count
        data.count += 1

        # check exceeding
        if data.count >= database["count"]:
            if await self.do_action(message, database):
                self.reset_flood(message)
                return True

        self.insert_flood(data, message, database)
        return False

    @classmethod
    def is_message_valid(cls, message) -> bool:
        _pre = [ContentType.NEW_CHAT_MEMBERS, ContentType.LEFT_CHAT_MEMBER]
        if message.content_type in _pre:
            return False
        elif message.chat.type in (ChatType.PRIVATE,):
            return False
        return True

    def get_flood(self, message) -> Optional[CacheModel]:
        if data := bredis.get(self.cache_key(message)):
            data = pickle.loads(data)
            return data
        return None

    def insert_flood(self, data: CacheModel, message: Message, database: dict):
        ex = (
            convert_time(database["time"])
            if database.get("time", None) is not None
            else None
        )
        return bredis.set(self.cache_key(message), pickle.dumps(data), ex=ex)

    def reset_flood(self, message):
        return bredis.delete(self.cache_key(message))

    def check_flood(self, message):
        return bredis.exists(self.cache_key(message))

    def set_state(self, message: Message):
        return bredis.set(
            self.state_cache_key.format(chat_id=message.chat.id), message.from_user.id
        )

    def get_state(self, message: Message):
        return bredis.get(self.state_cache_key.format(chat_id=message.chat.id))

    @classmethod
    def cache_key(cls, message: Message):
        return f"antiflood:{message.chat.id}:{message.from_user.id}"

    @classmethod
    async def do_action(cls, message: Message, database: dict):
        action = database["action"] if "action" in database else "ban"

        if action == "ban":
            return await ban_user(message.chat.id, message.from_user.id)
        elif action == "kick":
            return await kick_user(message.chat.id, message.from_user.id)
        elif action == "mute":
            return await mute_user(message.chat.id, message.from_user.id)
        else:
            return False

    async def on_pre_process_message(self, message: Message, _):
        log.debug(
            f"Enforcing flood control on {message.from_user.id} in {message.chat.id}"
        )
        if self.is_message_valid(message):
            if await is_user_admin(message.chat.id, message.from_user.id):
                return self.set_state(message)
            if (database := await get_data(message.chat.id)) is None:
                return

            if await self.enforcer(message, database):
                await message.delete()
                strings = await get_strings(message.chat.id, "antiflood")
                await message.answer(
                    strings["flood_exceeded"].format(
                        action=(
                            strings[database["action"]]
                            if "action" in database
                            else "banned"
                        ).capitalize(),
                        user=await get_user_link(message.from_user.id),
                    )
                )
                raise CancelHandler


@register(
    cmds=["setflood"], user_can_restrict_members=True, bot_can_restrict_members=True
)
@need_args_dec()
@chat_connection()
@get_strings_dec("antiflood")
async def setflood_command(message: Message, chat: dict, strings: dict):
    try:
        args = int(get_args(message)[0])
    except ValueError:
        return await message.reply(strings["invalid_args:setflood"])
    if args > 200:
        return await message.reply(strings["overflowed_count"])

    await AntiFloodConfigState.expiration_proc.set()
    redis.set(f"antiflood_setup:{chat['chat_id']}", args)
    await message.reply(
        strings["config_proc_1"],
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text=strings["cancel"],
                callback_data=cancel_state.new(user_id=message.from_user.id),
            )
        ),
    )


@register(
    state=AntiFloodConfigState.expiration_proc,
    content_types=ContentType.TEXT,
    allow_kwargs=True,
)
@chat_connection()
@get_strings_dec("antiflood")
async def antiflood_expire_proc(
    message: Message, chat: dict, strings: dict, state, **_
):
    try:
        if (time := message.text) not in (0, "0"):
            # just call for making sure its valid
            parsed_time = convert_time(time)
        else:
            time, parsed_time = None, None
    except (TypeError, ValueError):
        await message.reply(strings["invalid_time"])
    else:
        if not (data := redis.get(f'antiflood_setup:{chat["chat_id"]}')):
            await message.reply(strings["setup_corrupted"])
        else:
            await db.antiflood.update_one(
                {"chat_id": chat["chat_id"]},
                {"$set": {"time": time, "count": int(data)}},
                upsert=True,
            )
            await get_data.reset_cache(chat["chat_id"])
            kw = {"count": data}
            if time is not None:
                kw.update(
                    {
                        "time": format_timedelta(
                            parsed_time, locale=strings["language_info"]["babel"]
                        )
                    }
                )
            await message.reply(
                strings[
                    "setup_success" if time is not None else "setup_success:no_exp"
                ].format(**kw)
            )
    finally:
        await state.finish()


@register(cmds=["antiflood", "flood"], is_admin=True)
@chat_connection(admin=True)
@get_strings_dec("antiflood")
async def antiflood(message: Message, chat: dict, strings: dict):
    if not (data := await get_data(chat["chat_id"])):
        return await message.reply(strings["not_configured"])

    if message.get_args().lower() in ("off", "0", "no"):
        await db.antiflood.delete_one({"chat_id": chat["chat_id"]})
        await get_data.reset_cache(chat["chat_id"])
        return await message.reply(
            strings["turned_off"].format(chat_title=chat["chat_title"])
        )

    if data.get("time", None) is None:
        return await message.reply(
            strings["configuration_info"].format(
                action=strings[data["action"]] if "action" in data else strings["ban"],
                count=data["count"],
            )
        )
    return await message.reply(
        strings["configuration_info:with_time"].format(
            action=strings[data["action"]] if "action" in data else strings["ban"],
            count=data["count"],
            time=format_timedelta(
                convert_time(data["time"]), locale=strings["language_info"]["babel"]
            ),
        )
    )


@register(cmds=["setfloodaction"], user_can_restrict_members=True)
@need_args_dec()
@chat_connection(admin=True)
@get_strings_dec("antiflood")
async def setfloodaction(message: Message, chat: dict, strings: dict):
    SUPPORTED_ACTIONS = ["kick", "ban", "mute"]  # noqa
    if (action := message.get_args().lower()) not in SUPPORTED_ACTIONS:
        return await message.reply(
            strings["invalid_args"].format(
                supported_actions=", ".join(SUPPORTED_ACTIONS)
            )
        )

    await db.antiflood.update_one(
        {"chat_id": chat["chat_id"]}, {"$set": {"action": action}}, upsert=True
    )
    await get_data.reset_cache(message.chat.id)
    return await message.reply(strings["setfloodaction_success"].format(action=action))


async def __before_serving__(_):
    dp.middleware.setup(AntifloodEnforcer())


@register(cancel_state.filter(), f="cb")
async def cancel_state_cb(event: CallbackQuery):
    await event.message.delete()


@cached()
async def get_data(chat_id: int):
    return await db.antiflood.find_one({"chat_id": chat_id})


async def __export__(chat_id: int):
    data = await get_data(chat_id)
    if not data:
        return

    del data["_id"], data["chat_id"]
    return data


async def __import__(chat_id: int, data: dict):  # noqa
    await db.antiflood.update_one({"chat_id": chat_id}, {"$set": data})


__mod_name__ = "AntiFlood"

__help__ = """
You know how sometimes, people join, send 100 messages, and ruin your chat? With antiflood, that happens no more!

Antiflood allows you to take action on users that send more than x messages in a row.

<b>Admins only:</b>
- /antiflood: Gives you current configuration of antiflood in the chat
- /antiflood off: Disables Antiflood
- /setflood (limit): Sets flood limit

Replace (limit) with any integer, should be less than 200. When setting up, Daisy would ask you to send expiration time, if you dont understand what this expiration time for? User who sends specified limit of messages consecutively within this TIME, would be kicked, banned whatever the action is. if you dont want this TIME, wants to take action against those who exceeds specified limit without mattering TIME INTERVAL between the messages. you can reply to question with 0

<b>Configuring the time:</b>
<code>2m</code> = 2 minutes
<code>2h</code> = 2 hours
<code>2d</code> = 2 days

<b>Example:</b>
Me: <code>/setflood 10</code>
Daisy: <code>Please send expiration time [...]</code>
Me: <code>5m</code> (5 minutes)
DONE!

- /setfloodaction (action): Sets the action to taken when user exceeds flood limit

<b>Currently supported actions:</b>
<code>ban</code>
<code>mute</code>
<code>kick</code>
<i>More soon™</i>
"""
