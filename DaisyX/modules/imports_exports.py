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
import io
from datetime import datetime, timedelta

import rapidjson
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.input_file import InputFile
from babel.dates import format_timedelta

from DaisyX import OPERATORS, bot
from DaisyX.decorator import register
from DaisyX.services.redis import redis

from . import LOADED_MODULES
from .utils.connections import chat_connection
from .utils.language import get_strings_dec

VERSION = 5


# Waiting for import file state
class ImportFileWait(StatesGroup):
    waiting = State()


@register(cmds="export", user_admin=True)
@chat_connection(admin=True, only_groups=True)
@get_strings_dec("imports_exports")
async def export_chat_data(message, chat, strings):
    chat_id = chat["chat_id"]
    key = "export_lock:" + str(chat_id)
    if redis.get(key) and message.from_user.id not in OPERATORS:
        ttl = format_timedelta(
            timedelta(seconds=redis.ttl(key)), strings["language_info"]["babel"]
        )
        await message.reply(strings["exports_locked"] % ttl)
        return

    redis.set(key, 1)
    redis.expire(key, 7200)

    msg = await message.reply(strings["started_exporting"])
    data = {
        "general": {
            "chat_name": chat["chat_title"],
            "chat_id": chat_id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": VERSION,
        }
    }

    for module in [m for m in LOADED_MODULES if hasattr(m, "__export__")]:
        await asyncio.sleep(0)  # Switch to other events before continue
        if k := await module.__export__(chat_id):
            data.update(k)

    jfile = InputFile(
        io.StringIO(rapidjson.dumps(data, indent=2)), filename=f"{chat_id}_export.json"
    )
    text = strings["export_done"].format(chat_name=chat["chat_title"])
    await message.answer_document(jfile, text, reply=message.message_id)
    await msg.delete()


@register(cmds="import", user_admin=True)
@get_strings_dec("imports_exports")
async def import_reply(message, strings):
    if "document" in message:
        document = message.document
    else:
        if "reply_to_message" not in message:
            await ImportFileWait.waiting.set()
            await message.reply(strings["send_import_file"])
            return

        elif "document" not in message.reply_to_message:
            await message.reply(strings["rpl_to_file"])
            return
        document = message.reply_to_message.document

    await import_fun(message, document)


@register(
    state=ImportFileWait.waiting,
    content_types=types.ContentTypes.DOCUMENT,
    allow_kwargs=True,
)
async def import_state(message, state=None, **kwargs):
    await import_fun(message, message.document)
    await state.finish()


@chat_connection(admin=True, only_groups=True)
@get_strings_dec("imports_exports")
async def import_fun(message, document, chat, strings):
    chat_id = chat["chat_id"]
    key = "import_lock:" + str(chat_id)
    if redis.get(key) and message.from_user.id not in OPERATORS:
        ttl = format_timedelta(
            timedelta(seconds=redis.ttl(key)), strings["language_info"]["babel"]
        )
        await message.reply(strings["imports_locked"] % ttl)
        return

    redis.set(key, 1)
    redis.expire(key, 7200)

    msg = await message.reply(strings["started_importing"])
    if document["file_size"] > 52428800:
        await message.reply(strings["big_file"])
        return
    data = await bot.download_file_by_id(document.file_id, io.BytesIO())
    try:
        data = rapidjson.load(data)
    except ValueError:
        return await message.reply(strings["invalid_file"])

    if "general" not in data:
        await message.reply(strings["bad_file"])
        return

    file_version = data["general"]["version"]

    if file_version > VERSION:
        await message.reply(strings["file_version_so_new"])
        return

    imported = []
    for module in [m for m in LOADED_MODULES if hasattr(m, "__import__")]:
        module_name = module.__name__.replace("DaisyX.modules.", "")
        if module_name not in data:
            continue
        if not data[module_name]:
            continue

        imported.append(module_name)
        await asyncio.sleep(0)  # Switch to other events before continue
        await module.__import__(chat_id, data[module_name])

    await msg.edit_text(strings["import_done"])


__mod_name__ = "Backups"

__help__ = """
Sometimes you want to see all of your data in your chats or you want to copy your data to another chats or you even want to swift bots, in all these cases imports/exports for you!

<b>Available commands:</b>
- /export: Export chat's data to JSON file
- /import: Import JSON file to chat

<b>Notes:</b> Exporting / importing avaible every 2 hours to prevent flooding.
"""
