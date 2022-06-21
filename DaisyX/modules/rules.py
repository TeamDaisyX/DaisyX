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

from aiogram.dispatcher.filters import CommandStart

from DaisyX.decorator import register
from DaisyX.services.mongo import db

from .utils.connections import chat_connection
from .utils.disable import disableable_dec
from .utils.language import get_strings_dec
from .utils.notes import (
    ALLOWED_COLUMNS,
    BUTTONS,
    get_parsed_note_list,
    send_note,
    t_unparse_note_item,
)


@register(cmds=["setrules", "saverules"], user_admin=True)
@chat_connection(admin=True, only_groups=True)
@get_strings_dec("rules")
async def set_rules(message, chat, strings):
    chat_id = chat["chat_id"]

    # FIXME: documents are allow to saved (why?), check for args if no 'reply_to_message'
    note = await get_parsed_note_list(message, allow_reply_message=True, split_args=-1)
    note["chat_id"] = chat_id

    if (
        await db.rules.replace_one({"chat_id": chat_id}, note, upsert=True)
    ).modified_count > 0:
        text = strings["updated"]
    else:
        text = strings["saved"]

    await message.reply(text % chat["chat_title"])


@register(cmds="rules")
@disableable_dec("rules")
@chat_connection(only_groups=True)
@get_strings_dec("rules")
async def rules(message, chat, strings):
    chat_id = chat["chat_id"]
    send_id = message.chat.id

    if "reply_to_message" in message:
        rpl_id = message.reply_to_message.message_id
    else:
        rpl_id = message.message_id

    arg1 = args[0].lower() if len(args := message.get_args().split()) > 0 else None
    noformat = arg1 in ("noformat", "raw")

    if not (db_item := await db.rules.find_one({"chat_id": chat_id})):
        await message.reply(strings["not_found"])
        return

    text, kwargs = await t_unparse_note_item(
        message, db_item, chat_id, noformat=noformat
    )
    kwargs["reply_to"] = rpl_id

    await send_note(send_id, text, **kwargs)


@register(cmds="resetrules", user_admin=True)
@chat_connection(admin=True, only_groups=True)
@get_strings_dec("rules")
async def reset_rules(message, chat, strings):
    chat_id = chat["chat_id"]

    if (await db.rules.delete_one({"chat_id": chat_id})).deleted_count < 1:
        await message.reply(strings["not_found"])
        return

    await message.reply(strings["deleted"])


BUTTONS.update({"rules": "btn_rules"})


@register(CommandStart(re.compile("btn_rules")))
@get_strings_dec("rules")
async def rules_btn(message, strings):
    chat_id = (message.get_args().split("_"))[2]
    user_id = message.chat.id
    if not (db_item := await db.rules.find_one({"chat_id": int(chat_id)})):
        await message.answer(strings["not_found"])
        return

    text, kwargs = await t_unparse_note_item(message, db_item, chat_id)
    await send_note(user_id, text, **kwargs)


async def __export__(chat_id):
    rules = await db.rules.find_one({"chat_id": chat_id})
    if rules:
        del rules["_id"]
        del rules["chat_id"]

        return {"rules": rules}


async def __import__(chat_id, data):
    rules = data
    for column in [i for i in rules if i not in ALLOWED_COLUMNS]:
        del rules[column]

    rules["chat_id"] = chat_id
    await db.rules.replace_one({"chat_id": rules["chat_id"]}, rules, upsert=True)


__mod_name__ = "Rules"

__help__ = """
<b>Available Commands:</b>
- /setrules (rules): saves the rules (also works with reply)
- /rules: Shows the rules of chat if any!
- /resetrules: Resets group's rules
"""
