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

import pickle
import re
from contextlib import suppress
from typing import Union

from aiogram.dispatcher.handler import SkipHandler
from aiogram.types import CallbackQuery, Message
from aiogram.utils.exceptions import BadRequest, ChatNotFound, Unauthorized
from telethon.tl.functions.users import GetFullUserRequest

from DaisyX import OPERATORS, bot
from DaisyX.services.mongo import db
from DaisyX.services.redis import bredis
from DaisyX.services.telethon import tbot

from .language import get_string
from .message import get_arg


async def add_user_to_db(user):
    if hasattr(user, "user"):
        user = user.user

    new_user = {
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
    }

    user = await db.user_list.find_one({"user_id": new_user["user_id"]})
    if not user or user is None:
        user = new_user

    if "chats" not in user:
        new_user["chats"] = []
    if "user_lang" not in user:
        new_user["user_lang"] = "en"
        if hasattr(user, "user_lang"):
            new_user["user_lang"] = user.user_lang

    await db.user_list.update_one(
        {"user_id": user["user_id"]}, {"$set": new_user}, upsert=True
    )

    return new_user


async def get_user_by_id(user_id: int):
    if not user_id <= 2147483647:
        return None

    user = await db.user_list.find_one({"user_id": user_id})
    if not user:
        try:
            user = await add_user_to_db(await tbot(GetFullUserRequest(user_id)))
        except (ValueError, TypeError):
            user = None

    return user


async def get_id_by_nick(data):
    # Check if data is user_id
    user = await db.user_list.find_one({"username": data.replace("@", "")})
    if user:
        return user["user_id"]

    user = await tbot(GetFullUserRequest(data))
    return user


async def get_user_by_username(username):
    # Search username in database
    if "@" in username:
        # Remove '@'
        username = username[1:]

    user = await db.user_list.find_one({"username": username.lower()})

    # Ohnu, we don't have this user in DB
    if not user:
        try:
            user = await add_user_to_db(await tbot(GetFullUserRequest(username)))
        except (ValueError, TypeError):
            user = None

    return user


async def get_user_link(user_id, custom_name=None, md=False):
    user = await db.user_list.find_one({"user_id": user_id})

    if user:
        user_name = user["first_name"]
    else:
        try:
            user = await add_user_to_db(await tbot(GetFullUserRequest(int(user_id))))
        except (ValueError, TypeError):
            user_name = str(user_id)
        else:
            user_name = user["first_name"]

    if custom_name:
        user_name = custom_name

    if md:
        return "[{name}](tg://user?id={id})".format(name=user_name, id=user_id)
    else:
        return '<a href="tg://user?id={id}">{name}</a>'.format(
            name=user_name, id=user_id
        )


async def get_admins_rights(chat_id, force_update=False):
    key = "admin_cache:" + str(chat_id)
    if (alist := bredis.get(key)) and not force_update:
        return pickle.loads(alist)
    else:
        alist = {}
        admins = await bot.get_chat_administrators(chat_id)
        for admin in admins:
            user_id = admin["user"]["id"]
            alist[user_id] = {
                "status": admin["status"],
                "admin": True,
                "title": admin["custom_title"],
                "anonymous": admin["is_anonymous"],
                "can_change_info": admin["can_change_info"],
                "can_delete_messages": admin["can_delete_messages"],
                "can_invite_users": admin["can_invite_users"],
                "can_restrict_members": admin["can_restrict_members"],
                "can_pin_messages": admin["can_pin_messages"],
                "can_promote_members": admin["can_promote_members"],
            }

            with suppress(KeyError):  # Optional permissions
                alist[user_id]["can_post_messages"] = admin["can_post_messages"]

        bredis.set(key, pickle.dumps(alist))
        bredis.expire(key, 900)
    return alist


async def is_user_admin(chat_id, user_id):
    # User's pm should have admin rights
    if chat_id == user_id:
        return True

    if user_id in OPERATORS:
        return True

    # Workaround to support anonymous admins
    if user_id == 1087968824:
        return True

    try:
        admins = await get_admins_rights(chat_id)
    except BadRequest:
        return False
    else:
        if user_id in admins:
            return True
        else:
            return False


async def check_admin_rights(
    event: Union[Message, CallbackQuery], chat_id, user_id, rights
):
    # User's pm should have admin rights
    if chat_id == user_id:
        return True

    if user_id in OPERATORS:
        return True

    # Workaround to support anonymous admins
    if user_id == 1087968824:
        if not isinstance(event, Message):
            raise ValueError(
                f"Cannot extract signuature of anonymous admin from {type(event)}"
            )

        if not event.author_signature:
            return True

        for admin in (await get_admins_rights(chat_id)).values():
            if "title" in admin and admin["title"] == event.author_signature:
                for permission in rights:
                    if not admin[permission]:
                        return permission
        return True

    admin_rights = await get_admins_rights(chat_id)
    if user_id not in admin_rights:
        return False

    if admin_rights[user_id]["status"] == "creator":
        return True

    for permission in rights:
        if not admin_rights[user_id][permission]:
            return permission

    return True


async def check_group_admin(event, user_id, no_msg=False):
    if hasattr(event, "chat_id"):
        chat_id = event.chat_id
    elif hasattr(event, "chat"):
        chat_id = event.chat.id
    if await is_user_admin(chat_id, user_id) is True:
        return True
    else:
        if no_msg is False:
            await event.reply("You should be a admin to do it!")
        return False


async def is_chat_creator(event: Union[Message, CallbackQuery], chat_id, user_id):
    admin_rights = await get_admins_rights(chat_id)

    if user_id == 1087968824:
        _co, possible_creator = 0, None
        for admin in admin_rights.values():
            if admin["title"] == event.author_signature:
                _co += 1
                possible_creator = admin

        if _co > 1:
            await event.answer(
                await get_string(chat_id, "global", "unable_identify_creator")
            )
            raise SkipHandler

        if possible_creator["status"] == "creator":
            return True
        return False

    if user_id not in admin_rights:
        return False

    if admin_rights[user_id]["status"] == "creator":
        return True

    return False


async def get_user_by_text(message, text: str):
    # Get all entities
    entities = filter(
        lambda ent: ent["type"] == "text_mention" or ent["type"] == "mention",
        message.entities,
    )
    for entity in entities:
        # If username matches entity's text
        if text in entity.get_text(message.text):
            if entity.type == "mention":
                # This one entity is comes with mention by username, like @rDaisyBot
                return await get_user_by_username(text)
            elif entity.type == "text_mention":
                # This one is link mention, mostly used for users without an username
                return await get_user_by_id(entity.user.id)

    # Now let's try get user with user_id
    # We trying this not first because user link mention also can have numbers
    if text.isdigit():
        user_id = int(text)
        if user := await get_user_by_id(user_id):
            return user

    # Not found anything 😞
    return None


async def get_user(message, allow_self=False):
    args = message.text.split(None, 2)
    user = None

    # Only 1 way
    if len(args) < 2 and "reply_to_message" in message:
        return await get_user_by_id(message.reply_to_message.from_user.id)

    # Use default function to get user
    if len(args) > 1:
        user = await get_user_by_text(message, args[1])

    if not user and bool(message.reply_to_message):
        user = await get_user_by_id(message.reply_to_message.from_user.id)

    if not user and allow_self:
        # TODO: Fetch user from message instead of db?! less overhead
        return await get_user_by_id(message.from_user.id)

    # No args and no way to get user
    if not user and len(args) < 2:
        return None

    return user


async def get_user_and_text(message, **kwargs):
    args = message.text.split(" ", 2)
    user = await get_user(message, **kwargs)

    if len(args) > 1:
        if (test_user := await get_user_by_text(message, args[1])) == user:
            if test_user:
                print(len(args))
                if len(args) > 2:
                    return user, args[2]
                else:
                    return user, ""

    if len(args) > 1:
        return user, message.text.split(" ", 1)[1]
    else:
        return user, ""


async def get_users(message):
    args = message.text.split(None, 2)
    text = args[1]
    users = []

    for text in text.split("|"):
        if user := await get_user_by_text(message, text):
            users.append(user)

    return users


async def get_users_and_text(message):
    users = await get_users(message)
    args = message.text.split(None, 2)

    if len(args) > 1:
        return users, args[1]
    else:
        return users, ""


def get_user_and_text_dec(**dec_kwargs):
    def wrapped(func):
        async def wrapped_1(*args, **kwargs):
            message = args[0]
            if hasattr(message, "message"):
                message = message.message

            user, text = await get_user_and_text(message, **dec_kwargs)
            if not user:
                await message.reply("I can't get the user!")
                return
            else:
                return await func(*args, user, text, **kwargs)

        return wrapped_1

    return wrapped


def get_user_dec(**dec_kwargs):
    def wrapped(func):
        async def wrapped_1(*args, **kwargs):
            message = args[0]
            if hasattr(message, "message"):
                message = message.message

            user, text = await get_user_and_text(message, **dec_kwargs)
            if not bool(user):
                await message.reply("I can't get the user!")
                return
            else:
                return await func(*args, user, **kwargs)

        return wrapped_1

    return wrapped


def get_chat_dec(allow_self=False, fed=False):
    def wrapped(func):
        async def wrapped_1(*args, **kwargs):
            message = args[0]
            if hasattr(message, "message"):
                message = message.message

            arg = get_arg(message)
            if fed is True:
                if len(text := message.get_args().split()) > 1:
                    if text[0].count("-") == 4:
                        arg = text[1]
                    else:
                        arg = text[0]

            if arg.startswith("-") or arg.isdigit():
                chat = await db.chat_list.find_one({"chat_id": int(arg)})
                if not chat:
                    try:
                        chat = await bot.get_chat(arg)
                    except ChatNotFound:
                        return await message.reply(
                            "I couldn't find the chat/channel! Maybe I am not there!"
                        )
                    except Unauthorized:
                        return await message.reply(
                            "I couldn't access chat/channel! Maybe I was kicked from there!"
                        )
            elif arg.startswith("@"):
                chat = await db.chat_list.find_one(
                    {"chat_nick": re.compile(arg.strip("@"), re.IGNORECASE)}
                )
            elif allow_self is True:
                chat = await db.chat_list.find_one({"chat_id": message.chat.id})
            else:
                await message.reply("Please give me valid chat ID/username")
                return

            if not chat:
                await message.reply("I can't find any chats on given information!")
                return

            return await func(*args, chat, **kwargs)

        return wrapped_1

    return wrapped
