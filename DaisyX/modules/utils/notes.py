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

import html
import re
import sys
from datetime import datetime

from aiogram.types import Message
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import markdown
from babel.dates import format_date, format_datetime, format_time
from telethon.errors import (
    BadRequestError,
    ButtonUrlInvalidError,
    MediaEmptyError,
    MessageEmptyError,
)
from telethon.tl.custom import Button

import DaisyX.modules.utils.tmarkdown as tmarkdown
from DaisyX import BOT_USERNAME
from DaisyX.services.telethon import tbot

from ...utils.logger import log
from .language import get_chat_lang
from .message import get_args
from .tmarkdown import tbold, tcode, titalic, tlink, tpre, tstrikethrough, tunderline
from .user_details import get_user_link

BUTTONS = {}

ALLOWED_COLUMNS = ["parse_mode", "file", "text", "preview"]


def tparse_ent(ent, text, as_html=True):
    if not text:
        return text

    etype = ent.type
    offset = ent.offset
    length = ent.length

    if sys.maxunicode == 0xFFFF:
        return text[offset : offset + length]

    if not isinstance(text, bytes):
        entity_text = text.encode("utf-16-le")
    else:
        entity_text = text

    entity_text = entity_text[offset * 2 : (offset + length) * 2].decode("utf-16-le")

    if etype == "bold":
        method = markdown.hbold if as_html else tbold
        return method(entity_text)
    if etype == "italic":
        method = markdown.hitalic if as_html else titalic
        return method(entity_text)
    if etype == "pre":
        method = markdown.hpre if as_html else tpre
        return method(entity_text)
    if etype == "code":
        method = markdown.hcode if as_html else tcode
        return method(entity_text)
    if etype == "strikethrough":
        method = markdown.hstrikethrough if as_html else tstrikethrough
        return method(entity_text)
    if etype == "underline":
        method = markdown.hunderline if as_html else tunderline
        return method(entity_text)
    if etype == "url":
        return entity_text
    if etype == "text_link":
        method = markdown.hlink if as_html else tlink
        return method(entity_text, ent.url)
    if etype == "text_mention" and ent.user:
        return ent.user.get_mention(entity_text, as_html=as_html)

    return entity_text


def get_parsed_msg(message):
    if not message.text and not message.caption:
        return "", "md"

    text = message.caption or message.text

    mode = get_msg_parse(text)
    if mode == "html":
        as_html = True
    else:
        as_html = False

    entities = message.caption_entities or message.entities

    if not entities:
        return text, mode

    if sys.maxunicode != 0xFFFF:
        text = text.encode("utf-16-le")

    result = ""
    offset = 0

    for entity in sorted(entities, key=lambda item: item.offset):
        entity_text = tparse_ent(entity, text, as_html=as_html)

        if sys.maxunicode == 0xFFFF:
            part = text[offset : entity.offset]
            result += part + entity_text
        else:
            part = text[offset * 2 : entity.offset * 2].decode("utf-16-le")
            result += part + entity_text

        offset = entity.offset + entity.length

    if sys.maxunicode == 0xFFFF:
        result += text[offset:]
    else:
        result += text[offset * 2 :].decode("utf-16-le")

    result = re.sub(r"\[format:(\w+)\]", "", result)
    result = re.sub(r"%PARSEMODE_(\w+)", "", result)

    if not result:
        result = ""

    return result, mode


def get_msg_parse(text, default_md=True):
    if "[format:html]" in text or "%PARSEMODE_HTML" in text:
        return "html"
    elif "[format:none]" in text or "%PARSEMODE_NONE" in text:
        return "none"
    elif "[format:md]" in text or "%PARSEMODE_MD" in text:
        return "md"
    else:
        if not default_md:
            return None
        return "md"


def parse_button(data, name):
    raw_button = data.split("_")
    raw_btn_type = raw_button[0]

    pattern = re.match(r"btn(.+)(sm|cb|start)", raw_btn_type)
    if not pattern:
        return ""

    action = pattern.group(1)
    args = raw_button[1]

    if action in BUTTONS:
        text = f"\n[{name}](btn{action}:{args}*!repl!*)"
    else:
        if args:
            text = f"\n[{name}].(btn{action}:{args})"
        else:
            text = f"\n[{name}].(btn{action})"

    return text


def get_reply_msg_btns_text(message):
    text = ""
    for column in message.reply_markup.inline_keyboard:
        btn_num = 0
        for btn in column:
            btn_num += 1
            name = btn["text"]

            if "url" in btn:
                url = btn["url"]
                if "?start=" in url:
                    raw_btn = url.split("?start=")[1]
                    text += parse_button(raw_btn, name)
                else:
                    text += f"\n[{btn['text']}](btnurl:{btn['url']}*!repl!*)"
            elif "callback_data" in btn:
                text += parse_button(btn["callback_data"], name)

            if btn_num > 1:
                text = text.replace("*!repl!*", ":same")
            else:
                text = text.replace("*!repl!*", "")
    return text


async def get_msg_file(message):
    message_id = message.message_id

    tmsg = await tbot.get_messages(message.chat.id, ids=message_id)

    file_types = [
        "sticker",
        "photo",
        "document",
        "video",
        "audio",
        "video_note",
        "voice",
    ]
    for file_type in file_types:
        if file_type not in message:
            continue
        if not tmsg.file:
            # FIXME: NoneType is unexpected here
            raise Exception("Telegram refused to give file info!")
        return {"id": tmsg.file.id, "type": file_type}
    return None


async def get_parsed_note_list(message, allow_reply_message=True, split_args=1):
    note = {}
    if "reply_to_message" in message and allow_reply_message:
        # Get parsed reply msg text
        text, note["parse_mode"] = get_parsed_msg(message.reply_to_message)
        # Get parsed origin msg text
        text += " "
        to_split = "".join([" " + q for q in get_args(message)[:split_args]])
        if not to_split:
            to_split = " "
        text += get_parsed_msg(message)[0].partition(message.get_command() + to_split)[
            2
        ][1:]
        # Set parse_mode if origin msg override it
        if mode := get_msg_parse(message.text, default_md=False):
            note["parse_mode"] = mode

        # Get message keyboard
        if (
            "reply_markup" in message.reply_to_message
            and "inline_keyboard" in message.reply_to_message.reply_markup
        ):
            text += get_reply_msg_btns_text(message.reply_to_message)

        # Check on attachment
        if msg_file := await get_msg_file(message.reply_to_message):
            note["file"] = msg_file
    else:
        text, note["parse_mode"] = get_parsed_msg(message)
        if message.get_command() and message.get_args():
            # Remove cmd and arg from message's text
            text = re.sub(message.get_command() + r"\s?", "", text, 1)
            if split_args > 0:
                text = re.sub(re.escape(get_args(message)[0]) + r"\s?", "", text, 1)
        # Check on attachment
        if msg_file := await get_msg_file(message):
            note["file"] = msg_file

    if text.replace(" ", ""):
        note["text"] = text

    # Preview
    if "text" in note and re.search(r"[$|%]PREVIEW", note["text"]):
        note["text"] = re.sub(r"[$|%]PREVIEW", "", note["text"])
        note["preview"] = True

    return note


async def t_unparse_note_item(
    message, db_item, chat_id, noformat=None, event=None, user=None
):
    text = db_item["text"] if "text" in db_item else ""

    file_id = None
    preview = None

    if not user:
        user = message.from_user

    if "file" in db_item:
        file_id = db_item["file"]["id"]

    if noformat:
        markup = None
        if "parse_mode" not in db_item or db_item["parse_mode"] == "none":
            text += "\n%PARSEMODE_NONE"
        elif db_item["parse_mode"] == "html":
            text += "\n%PARSEMODE_HTML"

        if "preview" in db_item and db_item["preview"]:
            text += "\n%PREVIEW"

        db_item["parse_mode"] = None

    else:
        pm = True if message.chat.type == "private" else False
        text, markup = button_parser(chat_id, text, pm=pm)

        if not text and not file_id:
            text = ("#" + db_item["names"][0]) if "names" in db_item else "404"

        if "parse_mode" not in db_item or db_item["parse_mode"] == "none":
            db_item["parse_mode"] = None
        elif db_item["parse_mode"] == "md":
            text = await vars_parser(
                text, message, chat_id, md=True, event=event, user=user
            )
        elif db_item["parse_mode"] == "html":
            text = await vars_parser(
                text, message, chat_id, md=False, event=event, user=user
            )

        if "preview" in db_item and db_item["preview"]:
            preview = True

    return text, {
        "buttons": markup,
        "parse_mode": db_item["parse_mode"],
        "file": file_id,
        "link_preview": preview,
    }


async def send_note(send_id, text, **kwargs):
    if text:
        text = text[:4090]

    if "parse_mode" in kwargs and kwargs["parse_mode"] == "md":
        kwargs["parse_mode"] = tmarkdown

    try:
        return await tbot.send_message(send_id, text, **kwargs)

    except (ButtonUrlInvalidError, MessageEmptyError, MediaEmptyError):
        return await tbot.send_message(
            send_id, "I found this note invalid! Please update it (read Wiki)."
        )

    except BadRequestError:  # if reply message deleted
        del kwargs["reply_to"]
        return await tbot.send_message(send_id, text, **kwargs)

    except Exception as err:
        log.error("Something happened on sending note", exc_info=err)


def button_parser(chat_id, texts, pm=False, aio=False, row_width=None):
    buttons = InlineKeyboardMarkup(row_width=row_width) if aio else []
    pattern = r"\[(.+?)\]\((button|btn|#)(.+?)(:.+?|)(:same|)\)(\n|)"
    raw_buttons = re.findall(pattern, texts)
    text = re.sub(pattern, "", texts)
    btn = None
    for raw_button in raw_buttons:
        name = raw_button[0]
        action = (
            raw_button[1] if raw_button[1] not in ("button", "btn") else raw_button[2]
        )

        if raw_button[3]:
            argument = raw_button[3][1:].lower().replace("`", "")
        elif action in ("#"):
            argument = raw_button[2]
            print(raw_button[2])
        else:
            argument = ""

        if action in BUTTONS.keys():
            cb = BUTTONS[action]
            string = f"{cb}_{argument}_{chat_id}" if argument else f"{cb}_{chat_id}"
            if aio:
                start_btn = InlineKeyboardButton(
                    name, url=f"https://t.me/{BOT_USERNAME}?start=" + string
                )
                cb_btn = InlineKeyboardButton(name, callback_data=string)
            else:
                start_btn = Button.url(
                    name, f"https://t.me/{BOT_USERNAME}?start=" + string
                )
                cb_btn = Button.inline(name, string)

            if cb.endswith("sm"):
                btn = cb_btn if pm else start_btn
            elif cb.endswith("cb"):
                btn = cb_btn
            elif cb.endswith("start"):
                btn = start_btn
            elif cb.startswith("url"):
                # Workaround to make URLs case-sensitive TODO: make better
                argument = raw_button[3][1:].replace("`", "") if raw_button[3] else ""
                btn = Button.url(name, argument)
            elif cb.endswith("rules"):
                btn = start_btn
        elif action == "url":
            argument = raw_button[3][1:].replace("`", "") if raw_button[3] else ""
            if argument[0] == "/" and argument[1] == "/":
                argument = argument[2:]
            btn = (
                InlineKeyboardButton(name, url=argument)
                if aio
                else Button.url(name, argument)
            )
        else:
            # If btn not registred
            btn = None
            if argument:
                text += f"\n[{name}].(btn{action}:{argument})"
            else:
                text += f"\n[{name}].(btn{action})"
                continue

        if btn:
            if aio:
                buttons.insert(btn) if raw_button[4] else buttons.add(btn)
            else:
                if len(buttons) < 1 and raw_button[4]:
                    buttons.add(btn) if aio else buttons.append([btn])
                else:
                    buttons[-1].append(btn) if raw_button[4] else buttons.append([btn])

    if not aio and len(buttons) == 0:
        buttons = None

    if not text or text.isspace():  # TODO: Sometimes we can return text == ' '
        text = None

    return text, buttons


async def vars_parser(
    text, message, chat_id, md=False, event: Message = None, user=None
):
    if event is None:
        event = message

    if not text:
        return text

    language_code = await get_chat_lang(chat_id)
    current_datetime = datetime.now()

    first_name = html.escape(user.first_name, quote=False)
    last_name = html.escape(user.last_name or "", quote=False)
    user_id = (
        [user.id for user in event.new_chat_members][0]
        if "new_chat_members" in event and event.new_chat_members != []
        else user.id
    )
    mention = await get_user_link(user_id, md=md)

    if (
        hasattr(event, "new_chat_members")
        and event.new_chat_members
        and event.new_chat_members[0].username
    ):
        username = "@" + event.new_chat_members[0].username
    elif user.username:
        username = "@" + user.username
    else:
        username = mention

    chat_id = message.chat.id
    chat_name = html.escape(message.chat.title or "Local", quote=False)
    chat_nick = message.chat.username or chat_name

    current_date = html.escape(
        format_date(date=current_datetime, locale=language_code), quote=False
    )
    current_time = html.escape(
        format_time(time=current_datetime, locale=language_code), quote=False
    )
    current_timedate = html.escape(
        format_datetime(datetime=current_datetime, locale=language_code), quote=False
    )

    text = (
        text.replace("{first}", first_name)
        .replace("{last}", last_name)
        .replace("{fullname}", first_name + " " + last_name)
        .replace("{id}", str(user_id).replace("{userid}", str(user_id)))
        .replace("{mention}", mention)
        .replace("{username}", username)
        .replace("{chatid}", str(chat_id))
        .replace("{chatname}", str(chat_name))
        .replace("{chatnick}", str(chat_nick))
        .replace("{date}", str(current_date))
        .replace("{time}", str(current_time))
        .replace("{timedate}", str(current_timedate))
    )
    return text
