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

import difflib
import re
from contextlib import suppress
from datetime import datetime

from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.deep_linking import get_start_link
from aiogram.utils.exceptions import (
    BadRequest,
    MessageCantBeDeleted,
    MessageNotModified,
)
from babel.dates import format_datetime
from pymongo import ReplaceOne
from telethon.errors.rpcerrorlist import MessageDeleteForbiddenError

from DaisyX import bot
from DaisyX.decorator import register
from DaisyX.services.mongo import db
from DaisyX.services.redis import redis
from DaisyX.services.telethon import tbot

from .utils.connections import chat_connection, set_connected_command
from .utils.disable import disableable_dec
from .utils.language import get_string, get_strings_dec
from .utils.message import get_arg, need_args_dec
from .utils.notes import (
    ALLOWED_COLUMNS,
    BUTTONS,
    get_parsed_note_list,
    send_note,
    t_unparse_note_item,
)
from .utils.user_details import get_user_link

RESTRICTED_SYMBOLS_IN_NOTENAMES = [
    ":",
    "**",
    "__",
    "`",
    "#",
    '"',
    "[",
    "]",
    "'",
    "$",
    "||",
]


async def get_similar_note(chat_id, note_name):
    all_notes = []
    async for note in db.notes.find({"chat_id": chat_id}):
        all_notes.extend(note["names"])

    if len(all_notes) > 0:
        check = difflib.get_close_matches(note_name, all_notes)
        if len(check) > 0:
            return check[0]

    return None


def clean_notes(func):
    async def wrapped_1(*args, **kwargs):
        event = args[0]

        message = await func(*args, **kwargs)
        if not message:
            return

        if event.chat.type == "private":
            return

        chat_id = event.chat.id

        data = await db.clean_notes.find_one({"chat_id": chat_id})
        if not data:
            return

        if data["enabled"] is not True:
            return

        if "msgs" in data:
            with suppress(MessageDeleteForbiddenError):
                await tbot.delete_messages(chat_id, data["msgs"])

        msgs = []
        if hasattr(message, "message_id"):
            msgs.append(message.message_id)
        else:
            msgs.append(message.id)

        msgs.append(event.message_id)

        await db.clean_notes.update_one({"chat_id": chat_id}, {"$set": {"msgs": msgs}})

    return wrapped_1


@register(cmds="save", user_admin=True, user_can_change_info=True)
@need_args_dec()
@chat_connection(admin=True)
@get_strings_dec("notes")
async def save_note(message, chat, strings):
    chat_id = chat["chat_id"]
    arg = get_arg(message).lower()
    if arg[0] == "#":
        arg = arg[1:]

    sym = None
    if any((sym := s) in arg for s in RESTRICTED_SYMBOLS_IN_NOTENAMES):
        await message.reply(strings["notename_cant_contain"].format(symbol=sym))
        return

    note_names = arg.split("|")

    note = await get_parsed_note_list(message)

    note["names"] = note_names
    note["chat_id"] = chat_id

    if "text" not in note and "file" not in note:
        await message.reply(strings["blank_note"])
        return

    if old_note := await db.notes.find_one(
        {"chat_id": chat_id, "names": {"$in": note_names}}
    ):
        text = strings["note_updated"]
        if "created_date" in old_note:
            note["created_date"] = old_note["created_date"]
            note["created_user"] = old_note["created_user"]
        note["edited_date"] = datetime.now()
        note["edited_user"] = message.from_user.id
    else:
        text = strings["note_saved"]
        note["created_date"] = datetime.now()
        note["created_user"] = message.from_user.id

    await db.notes.replace_one(
        {"_id": old_note["_id"]} if old_note else note, note, upsert=True
    )

    text += strings["you_can_get_note"]
    text = text.format(note_name=note_names[0], chat_title=chat["chat_title"])
    if len(note_names) > 1:
        text += strings["note_aliases"]
        for notename in note_names:
            text += f" <code>#{notename}</code>"

    await message.reply(text)


@get_strings_dec("notes")
async def get_note(
    message,
    strings,
    note_name=None,
    db_item=None,
    chat_id=None,
    send_id=None,
    rpl_id=None,
    noformat=False,
    event=None,
    user=None,
):
    if not chat_id:
        chat_id = message.chat.id

    if not send_id:
        send_id = message.chat.id

    if rpl_id is False:
        rpl_id = None
    elif not rpl_id:
        rpl_id = message.message_id

    if not db_item and not (
        db_item := await db.notes.find_one(
            {"chat_id": chat_id, "names": {"$in": [note_name]}}
        )
    ):
        await bot.send_message(chat_id, strings["no_note"], reply_to_message_id=rpl_id)
        return

    text, kwargs = await t_unparse_note_item(
        message, db_item, chat_id, noformat=noformat, event=event, user=user
    )
    kwargs["reply_to"] = rpl_id

    return await send_note(send_id, text, **kwargs)


@register(cmds="get")
@disableable_dec("get")
@need_args_dec()
@chat_connection(command="get")
@get_strings_dec("notes")
@clean_notes
async def get_note_cmd(message, chat, strings):
    chat_id = chat["chat_id"]
    chat_name = chat["chat_title"]

    note_name = get_arg(message).lower()
    if note_name[0] == "#":
        note_name = note_name[1:]

    if "reply_to_message" in message:
        rpl_id = message.reply_to_message.message_id
        user = message.reply_to_message.from_user
    else:
        rpl_id = message.message_id
        user = message.from_user

    if not (
        note := await db.notes.find_one(
            {"chat_id": int(chat_id), "names": {"$in": [note_name]}}
        )
    ):
        text = strings["cant_find_note"].format(chat_name=chat_name)
        if alleged_note_name := await get_similar_note(chat_id, note_name):
            text += strings["u_mean"].format(note_name=alleged_note_name)
        await message.reply(text)
        return

    noformat = False
    if len(args := message.text.split(" ")) > 2:
        arg2 = args[2].lower()
        noformat = arg2 in ("noformat", "raw")

    return await get_note(
        message, db_item=note, rpl_id=rpl_id, noformat=noformat, user=user
    )


@register(regexp=r"^#([\w-]+)", allow_kwargs=True)
@disableable_dec("get")
@chat_connection(command="get")
@clean_notes
async def get_note_hashtag(message, chat, regexp=None, **kwargs):
    chat_id = chat["chat_id"]

    note_name = regexp.group(1).lower()
    if not (
        note := await db.notes.find_one(
            {"chat_id": int(chat_id), "names": {"$in": [note_name]}}
        )
    ):
        return

    if "reply_to_message" in message:
        rpl_id = message.reply_to_message.message_id
        user = message.reply_to_message.from_user
    else:
        rpl_id = message.message_id
        user = message.from_user

    return await get_note(message, db_item=note, rpl_id=rpl_id, user=user)


@register(cmds=["notes", "saved"])
@disableable_dec("notes")
@chat_connection(command="notes")
@get_strings_dec("notes")
@clean_notes
async def get_notes_list_cmd(message, chat, strings):
    if (
        await db.privatenotes.find_one({"chat_id": chat["chat_id"]})
        and message.chat.id == chat["chat_id"]
    ):  # Workaround to avoid sending PN to connected PM
        text = strings["notes_in_private"]
        if not (keyword := message.get_args()):
            keyword = None
        button = InlineKeyboardMarkup().add(
            InlineKeyboardButton(
                text="Click here",
                url=await get_start_link(f"notes_{chat['chat_id']}_{keyword}"),
            )
        )
        return await message.reply(
            text, reply_markup=button, disable_web_page_preview=True
        )
    else:
        return await get_notes_list(message, chat=chat)


@get_strings_dec("notes")
async def get_notes_list(message, strings, chat, keyword=None, pm=False):
    text = strings["notelist_header"].format(chat_name=chat["chat_title"])

    notes = (
        await db.notes.find({"chat_id": chat["chat_id"]})
        .sort("names", 1)
        .to_list(length=300)
    )
    if not notes:
        return await message.reply(
            strings["notelist_no_notes"].format(chat_title=chat["chat_title"])
        )

    async def search_notes(request):
        nonlocal notes, text, note, note_name
        text += "\n" + strings["notelist_search"].format(request=request)
        all_notes = notes
        notes = []
        for note in all_notes:
            for note_name in note["names"]:
                if re.search(request, note_name):
                    notes.append(note)
        if len(notes) <= 0:
            return await message.reply(strings["no_notes_pattern"] % request)

    # Search
    if keyword:
        await search_notes(keyword)
    if len(keyword := message.get_args()) > 0 and pm is False:
        await search_notes(keyword)

    if len(notes) > 0:
        for note in notes:
            text += "\n-"
            for note_name in note["names"]:
                text += f" <code>#{note_name}</code>"
        text += strings["you_can_get_note"]

        try:
            return await message.reply(text)
        except BadRequest:
            await message.answer(text)


@register(cmds="search")
@chat_connection()
@get_strings_dec("notes")
@clean_notes
async def search_in_note(message, chat, strings):
    request = message.get_args()
    text = strings["search_header"].format(
        chat_name=chat["chat_title"], request=request
    )

    notes = db.notes.find(
        {"chat_id": chat["chat_id"], "text": {"$regex": request, "$options": "i"}}
    ).sort("names", 1)
    for note in (check := await notes.to_list(length=300)):
        text += "\n-"
        for note_name in note["names"]:
            text += f" <code>#{note_name}</code>"
    text += strings["you_can_get_note"]
    if not check:
        return await message.reply(
            strings["notelist_no_notes"].format(chat_title=chat["chat_title"])
        )
    return await message.reply(text)


@register(cmds=["clear", "delnote"], user_admin=True, user_can_change_info=True)
@chat_connection(admin=True)
@need_args_dec()
@get_strings_dec("notes")
async def clear_note(message, chat, strings):
    note_names = get_arg(message).lower().split("|")

    removed = ""
    not_removed = ""
    for note_name in note_names:
        if note_name[0] == "#":
            note_name = note_name[1:]

        if not (
            note := await db.notes.find_one(
                {"chat_id": chat["chat_id"], "names": {"$in": [note_name]}}
            )
        ):
            if len(note_names) <= 1:
                text = strings["cant_find_note"].format(chat_name=chat["chat_title"])
                if alleged_note_name := await get_similar_note(
                    chat["chat_id"], note_name
                ):
                    text += strings["u_mean"].format(note_name=alleged_note_name)
                await message.reply(text)
                return
            else:
                not_removed += " #" + note_name
                continue

        await db.notes.delete_one({"_id": note["_id"]})
        removed += " #" + note_name

    if len(note_names) > 1:
        text = strings["note_removed_multiple"].format(
            chat_name=chat["chat_title"], removed=removed
        )
        if not_removed:
            text += strings["not_removed_multiple"].format(not_removed=not_removed)
        await message.reply(text)
    else:
        await message.reply(
            strings["note_removed"].format(
                note_name=note_name, chat_name=chat["chat_title"]
            )
        )


@register(cmds="clearall", user_admin=True, user_can_change_info=True)
@chat_connection(admin=True)
@get_strings_dec("notes")
async def clear_all_notes(message, chat, strings):
    # Ensure notes count
    if not await db.notes.find_one({"chat_id": chat["chat_id"]}):
        await message.reply(
            strings["notelist_no_notes"].format(chat_title=chat["chat_title"])
        )
        return

    text = strings["clear_all_text"].format(chat_name=chat["chat_title"])
    buttons = InlineKeyboardMarkup()
    buttons.add(
        InlineKeyboardButton(
            strings["clearall_btn_yes"], callback_data="clean_all_notes_cb"
        )
    )
    buttons.add(
        InlineKeyboardButton(strings["clearall_btn_no"], callback_data="cancel")
    )
    await message.reply(text, reply_markup=buttons)


@register(regexp="clean_all_notes_cb", f="cb", is_admin=True, user_can_change_info=True)
@chat_connection(admin=True)
@get_strings_dec("notes")
async def clear_all_notes_cb(event, chat, strings):
    num = (await db.notes.delete_many({"chat_id": chat["chat_id"]})).deleted_count

    text = strings["clearall_done"].format(num=num, chat_name=chat["chat_title"])
    await event.message.edit_text(text)


@register(cmds="noteinfo", user_admin=True)
@chat_connection()
@need_args_dec()
@get_strings_dec("notes")
@clean_notes
async def note_info(message, chat, strings):
    note_name = get_arg(message).lower()
    if note_name[0] == "#":
        note_name = note_name[1:]

    if not (
        note := await db.notes.find_one(
            {"chat_id": chat["chat_id"], "names": {"$in": [note_name]}}
        )
    ):
        text = strings["cant_find_note"].format(chat_name=chat["chat_title"])
        if alleged_note_name := await get_similar_note(chat["chat_id"], note_name):
            text += strings["u_mean"].format(note_name=alleged_note_name)
        return await message.reply(text)

    text = strings["note_info_title"]

    note_names = ""
    for note_name in note["names"]:
        note_names += f" <code>#{note_name}</code>"

    text += strings["note_info_note"] % note_names
    text += strings["note_info_content"] % (
        "text" if "file" not in note else note["file"]["type"]
    )

    if "parse_mode" not in note or note["parse_mode"] == "md":
        parse_mode = "Markdown"
    elif note["parse_mode"] == "html":
        parse_mode = "HTML"
    elif note["parse_mode"] == "none":
        parse_mode = "None"
    else:
        raise TypeError()

    text += strings["note_info_parsing"] % parse_mode

    if "created_date" in note:
        text += strings["note_info_created"].format(
            date=format_datetime(
                note["created_date"], locale=strings["language_info"]["babel"]
            ),
            user=await get_user_link(note["created_user"]),
        )

    if "edited_date" in note:
        text += strings["note_info_updated"].format(
            date=format_datetime(
                note["edited_date"], locale=strings["language_info"]["babel"]
            ),
            user=await get_user_link(note["edited_user"]),
        )

    return await message.reply(text)


BUTTONS.update({"note": "btnnotesm", "#": "btnnotesm"})


@register(regexp=r"btnnotesm_(\w+)_(.*)", f="cb", allow_kwargs=True)
@get_strings_dec("notes")
async def note_btn(event, strings, regexp=None, **kwargs):
    chat_id = int(regexp.group(2))
    user_id = event.from_user.id
    note_name = regexp.group(1).lower()

    if not (
        note := await db.notes.find_one(
            {"chat_id": chat_id, "names": {"$in": [note_name]}}
        )
    ):
        await event.answer(strings["no_note"])
        return

    with suppress(MessageCantBeDeleted):
        await event.message.delete()
    await get_note(
        event.message,
        db_item=note,
        chat_id=chat_id,
        send_id=user_id,
        rpl_id=None,
        event=event,
    )


@register(CommandStart(re.compile(r"btnnotesm")), allow_kwargs=True)
@get_strings_dec("notes")
async def note_start(message, strings, regexp=None, **kwargs):
    # Don't even ask what it means, mostly it workaround to support note names with _
    args = re.search(r"^([a-zA-Z0-9]+)_(.*?)(-\d+)$", message.get_args())
    chat_id = int(args.group(3))
    user_id = message.from_user.id
    note_name = args.group(2).strip("_")

    if not (
        note := await db.notes.find_one(
            {"chat_id": chat_id, "names": {"$in": [note_name]}}
        )
    ):
        await message.reply(strings["no_note"])
        return

    await get_note(message, db_item=note, chat_id=chat_id, send_id=user_id, rpl_id=None)


@register(cmds="start", only_pm=True)
@get_strings_dec("connections")
async def btn_note_start_state(message, strings):
    key = "btn_note_start_state:" + str(message.from_user.id)
    if not (cached := redis.hgetall(key)):
        return

    chat_id = int(cached["chat_id"])
    user_id = message.from_user.id
    note_name = cached["notename"]

    note = await db.notes.find_one({"chat_id": chat_id, "names": {"$in": [note_name]}})
    await get_note(message, db_item=note, chat_id=chat_id, send_id=user_id, rpl_id=None)

    redis.delete(key)


@register(cmds="privatenotes", is_admin=True, user_can_change_info=True)
@chat_connection(admin=True)
@get_strings_dec("notes")
async def private_notes_cmd(message, chat, strings):
    chat_id = chat["chat_id"]
    chat_name = chat["chat_title"]
    text = str

    try:
        (text := "".join(message.text.split()[1]).lower())
    except IndexError:
        pass

    enabling = ["true", "enable", "on"]
    disabling = ["false", "disable", "off"]
    if database := await db.privatenotes.find_one({"chat_id": chat_id}):
        if text in enabling:
            await message.reply(strings["already_enabled"] % chat_name)
            return
    if text in enabling:
        await db.privatenotes.insert_one({"chat_id": chat_id})
        await message.reply(strings["enabled_successfully"] % chat_name)
    elif text in disabling:
        if not database:
            await message.reply(strings["not_enabled"])
            return
        await db.privatenotes.delete_one({"_id": database["_id"]})
        await message.reply(strings["disabled_successfully"] % chat_name)
    else:
        # Assume admin asked for current state
        if database:
            state = strings["enabled"]
        else:
            state = strings["disabled"]
        await message.reply(
            strings["current_state_info"].format(state=state, chat=chat_name)
        )


@register(cmds="cleannotes", is_admin=True, user_can_change_info=True)
@chat_connection(admin=True)
@get_strings_dec("notes")
async def clean_notes(message, chat, strings):
    disable = ["no", "off", "0", "false", "disable"]
    enable = ["yes", "on", "1", "true", "enable"]

    chat_id = chat["chat_id"]

    arg = get_arg(message)
    if arg and arg.lower() in enable:
        await db.clean_notes.update_one(
            {"chat_id": chat_id}, {"$set": {"enabled": True}}, upsert=True
        )
        text = strings["clean_notes_enable"].format(chat_name=chat["chat_title"])
    elif arg and arg.lower() in disable:
        await db.clean_notes.update_one(
            {"chat_id": chat_id}, {"$set": {"enabled": False}}, upsert=True
        )
        text = strings["clean_notes_disable"].format(chat_name=chat["chat_title"])
    else:
        data = await db.clean_notes.find_one({"chat_id": chat_id})
        if data and data["enabled"] is True:
            text = strings["clean_notes_enabled"].format(chat_name=chat["chat_title"])
        else:
            text = strings["clean_notes_disabled"].format(chat_name=chat["chat_title"])

    await message.reply(text)


@register(CommandStart(re.compile("notes")))
@get_strings_dec("notes")
async def private_notes_func(message, strings):
    args = message.get_args().split("_")
    chat_id = args[1]
    keyword = args[2] if args[2] != "None" else None
    await set_connected_command(message.from_user.id, int(chat_id), ["get", "notes"])
    chat = await db.chat_list.find_one({"chat_id": int(chat_id)})
    await message.answer(strings["privatenotes_notif"].format(chat=chat["chat_title"]))
    await get_notes_list(message, chat=chat, keyword=keyword, pm=True)


async def __stats__():
    text = "* <code>{}</code> total notes\n".format(await db.notes.count_documents({}))
    return text


async def __export__(chat_id):
    data = []
    notes = (
        await db.notes.find({"chat_id": chat_id}).sort("names", 1).to_list(length=300)
    )
    for note in notes:
        del note["_id"]
        del note["chat_id"]
        note["created_date"] = str(note["created_date"])
        if "edited_date" in note:
            note["edited_date"] = str(note["edited_date"])
        data.append(note)

    return {"notes": data}


ALLOWED_COLUMNS_NOTES = ALLOWED_COLUMNS + [
    "names",
    "created_date",
    "created_user",
    "edited_date",
    "edited_user",
]


async def __import__(chat_id, data):
    if not data:
        return

    new = []
    for note in data:

        # File ver 1 to 2
        if "name" in note:
            note["names"] = [note["name"]]
            del note["name"]

        for item in [i for i in note if i not in ALLOWED_COLUMNS_NOTES]:
            del note[item]

        note["chat_id"] = chat_id
        note["created_date"] = datetime.fromisoformat(note["created_date"])
        if "edited_date" in note:
            note["edited_date"] = datetime.fromisoformat(note["edited_date"])
        new.append(
            ReplaceOne(
                {"chat_id": note["chat_id"], "names": {"$in": [note["names"][0]]}},
                note,
                upsert=True,
            )
        )

    await db.notes.bulk_write(new)


async def filter_handle(message, chat, data):
    chat_id = chat["chat_id"]
    read_chat_id = message.chat.id
    note_name = data["note_name"]
    note = await db.notes.find_one({"chat_id": chat_id, "names": {"$in": [note_name]}})
    await get_note(
        message, db_item=note, chat_id=chat_id, send_id=read_chat_id, rpl_id=None
    )


async def setup_start(message):
    text = await get_string(message.chat.id, "notes", "filters_setup_start")
    with suppress(MessageNotModified):
        await message.edit_text(text)


async def setup_finish(message, data):
    note_name = message.text.split(" ", 1)[0].split()[0]

    if not (await db.notes.find_one({"chat_id": data["chat_id"], "names": note_name})):
        await message.reply("no such note!")
        return

    return {"note_name": note_name}


__filters__ = {
    "get_note": {
        "title": {"module": "notes", "string": "filters_title"},
        "handle": filter_handle,
        "setup": {"start": setup_start, "finish": setup_finish},
        "del_btn_name": lambda msg, data: f"Get note: {data['note_name']}",
    }
}


__mod_name__ = "Notes"

__help__ = """
Sometimes you need to save some data, like text or pictures. With notes, you can save any types of Telegram's data in your chats.
Also notes perfectly working in PM with Daisy.

<b>Available commands:</b>
- /save (name) (data): Saves the note.
- #(name) or /get (name): Get the note registered to that word.
- /clear (name): deletes the note.
- /notes or /saved: Lists all notes.
- /noteinfo (name): Shows detailed info about the note.
- /search (search pattern): Search text in notes
- /clearall: Clears all notes

<b>Only in groups:</b>
- /privatenotes (on/off): Redirect user in PM to see notes
- /cleannotes (on/off): Will clean old notes messages

<b>Examples:</b>
An example of how to save a note would be via:
<code>/save data This is example note!</code>
Now, anyone using <code>/get data</code>, or <code>#data</code> will be replied to with This is example note!.

<b>Saving pictures and other non-text data:</b>
If you want to save an image, gif, or sticker, or any other data, do the following:
<code>/save word</code> while replying to a sticker or whatever data you'd like. Now, the note at <code>#word</code> contains a sticker which will be sent as a reply.

<b>Removing many notes per one request:</b>
To remove many notes you can use the /clear command, just place all note names which you want to remove as argument of the command, use | as seprator, for example:
<code>/clear note1|note2|note3</code>

<b>Notes aliases:</b>
You can save note with many names, example:
<code>/save name1|name2|name3</code>
That will save a note with 3 different names, by any you can /get note, that can be useful if users in your chat trying to get notes which exits by other names.

<b>Notes buttons and variables:</b>
Notes support inline buttons, send /buttonshelp to get started with using it.
Variables are special words which will be replaced by actual info like if you add <code>{id}</code> in your note it will be replaced by user ID which asked note. Send /variableshelp to get started with using it.

<b>Notes formatting and settings:</b>
Every note can contain special settings, for example you can change formatting method to HTML by <code>%PARSEMODE_HTML</code> and fully disable it by <code>%PARSEMODE_NONE</code> ( By default formatting is Markdown or the same formatting Telegram supports )

<code>%PARSEMODE_(HTML, NONE)</code>: Change the note formatting
<code>%PREVIEW</code>: Enables the links preview in saved note

<b>Saving notes from other Marie style bots:</b>
Sophie can save notes from other bots, just reply /save on the saved message from another bot, saving pictures and buttons supported aswell.

<b>Retrieving notes without the formatting:</b>
To retrieve a note without the formatting, use <code>/get (name) raw</code> or <code>/get (name) noformat</code>
This will retrieve the note and send it without formatting it; getting you the raw note, allowing you to make easy edits.
"""
