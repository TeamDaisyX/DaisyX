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
from contextlib import suppress
from datetime import datetime

import wikipedia

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.exceptions import (
    BadRequest,
    MessageNotModified,
    MessageToDeleteNotFound,
)

from DaisyX.decorator import register

from .utils.disable import disableable_dec
from .utils.httpx import http
from .utils.language import get_strings_dec
from .utils.message import get_args_str
from .utils.notes import get_parsed_note_list, send_note, t_unparse_note_item
from .utils.user_details import is_user_admin


@register(cmds="buttonshelp", no_args=True, only_pm=True)
async def buttons_help(message):
    await message.reply(
        """
<b>Buttons:</b>
Here you will know how to setup buttons in your note, welcome note, etc...

There are different types of buttons!

<i>Due to current Implementation adding invalid button syntax to your note will raise error! This will be fixed in next major version.</i>

<b>Did you know?</b>
You could save buttons in same row using this syntax
<code>[Button](btn{mode}:{args if any}:same)</code>
(adding <code>:same</code> like that does the job.)

<b>Button Note:</b>
<i>Don't confuse this title with notes with buttons</i> 😜

This types of button will allow you to show specific notes to users when they click on buttons!

You can save note with button note without any hassle by adding below line to your note ( Don't forget to replace <code>notename</code> according to you 😀)

<code>[Button Name](btnnote:notename)</code>

<b>URL Button:</b>
Ah as you guessed! This method is used to add URL button to your note. With this you can redirect users to your website or even redirecting them to any channel, chat or messages!

You can add URL button by adding following syntax to your note

<code>[Button Name](btnurl:https://your.link.here)</code>

<b>Button rules:</b>
Well in v2 we introduced some changes, rules are now saved seperately unlike saved as note before v2 so it require seperate button method!

You can use this button method for including Rules button in your welcome messages, filters etc.. literally anywhere*

You use this button with adding following syntax to your message which support formatting!
<code>[Button Name](btnrules)</code>
    """
    )


@register(cmds="variableshelp", no_args=True, only_pm=True)
async def buttons_help(message):
    await message.reply(
        """
<b>Variables:</b>
Variables are special words which will be replaced by actual info

<b>Avaible variables:</b>
<code>{first}</code>: User's first name
<code>{last}</code>: User's last name
<code>{fullname}</code>: User's full name
<code>{id}</code>: User's ID
<code>{mention}</code>: Mention the user using first name
<code>{username}</code>: Get the username, if user don't have username will be returned mention
<code>{chatid}</code>: Chat's ID
<code>{chatname}</code>: Chat name
<code>{chatnick}</code>: Chat username
    """
    )


@register(cmds="wiki")
@disableable_dec("wiki")
async def wiki(message):
    args = get_args_str(message)
    wikipedia.set_lang("en")
    try:
        pagewiki = wikipedia.page(args)
    except wikipedia.exceptions.PageError as e:
        await message.reply(f"No results found!\nError: <code>{e}</code>")
        return
    except wikipedia.exceptions.DisambiguationError as refer:
        refer = str(refer).split("\n")
        if len(refer) >= 6:
            batas = 6
        else:
            batas = len(refer)
        text = ""
        for x in range(batas):
            if x == 0:
                text += refer[x] + "\n"
            else:
                text += "- `" + refer[x] + "`\n"
        await message.reply(text)
        return
    except IndexError:
        msg.reply_text("Write a message to search from wikipedia sources.")
        return
    title = pagewiki.title
    summary = pagewiki.summary
    button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔧 More Info...", url=wikipedia.page(args).url)
    )
    await message.reply(
        ("The result of {} is:\n\n<b>{}</b>\n{}").format(args, title, summary),
        reply_markup=button,
    )


@register(cmds="github")
@disableable_dec("github")
async def github(message):
    text = message.text[len("/github ") :]
    response = await http.get(f"https://api.github.com/users/{text}")
    usr = response.json()

    if usr.get("login"):
        text = f"<b>Username:</b> <a href='https://github.com/{usr['login']}'>{usr['login']}</a>"

        whitelist = [
            "name",
            "id",
            "type",
            "location",
            "blog",
            "bio",
            "followers",
            "following",
            "hireable",
            "public_gists",
            "public_repos",
            "email",
            "company",
            "updated_at",
            "created_at",
        ]

        difnames = {
            "id": "Account ID",
            "type": "Account type",
            "created_at": "Account created at",
            "updated_at": "Last updated",
            "public_repos": "Public Repos",
            "public_gists": "Public Gists",
        }

        goaway = [None, 0, "null", ""]

        for x, y in usr.items():
            if x in whitelist:
                x = difnames.get(x, x.title())

                if x in ("Account created at", "Last updated"):
                    y = datetime.strptime(y, "%Y-%m-%dT%H:%M:%SZ")

                if y not in goaway:
                    if x == "Blog":
                        x = "Website"
                        y = f"<a href='{y}'>Here!</a>"
                        text += "\n<b>{}:</b> {}".format(x, y)
                    else:
                        text += "\n<b>{}:</b> <code>{}</code>".format(x, y)
        reply_text = text
    else:
        reply_text = "User not found. Make sure you entered valid username!"
    await message.reply(reply_text, disable_web_page_preview=True)


@register(cmds="ip")
@disableable_dec("ip")
async def ip(message):
    try:
        ip = message.text.split(maxsplit=1)[1]
    except IndexError:
        await message.reply(f"Apparently you forgot something!")
        return

    response = await http.get(f"http://ip-api.com/json/{ip}")
    if response.status_code == 200:
        lookup_json = response.json()
    else:
        await message.reply(
            f"An error occurred when looking for <b>{ip}</b>: <b>{response.status_code}</b>"
        )
        return

    fixed_lookup = {}

    for key, value in lookup_json.items():
        special = {
            "lat": "Latitude",
            "lon": "Longitude",
            "isp": "ISP",
            "as": "AS",
            "asname": "AS name",
        }
        if key in special:
            fixed_lookup[special[key]] = str(value)
            continue

        key = re.sub(r"([a-z])([A-Z])", r"\g<1> \g<2>", key)
        key = key.capitalize()

        if not value:
            value = "None"

        fixed_lookup[key] = str(value)

    text = ""

    for key, value in fixed_lookup.items():
        text = text + f"<b>{key}:</b> <code>{value}</code>\n"

    await message.reply(text)


@register(cmds="cancel", state="*", allow_kwargs=True)
async def cancel_handle(message, state, **kwargs):
    await state.finish()
    await message.reply("Cancelled.")


async def delmsg_filter_handle(message, chat, data):
    if await is_user_admin(data["chat_id"], message.from_user.id):
        return
    with suppress(MessageToDeleteNotFound):
        await message.delete()


async def replymsg_filter_handler(message, chat, data):
    text, kwargs = await t_unparse_note_item(
        message, data["reply_text"], chat["chat_id"]
    )
    kwargs["reply_to"] = message.message_id
    with suppress(BadRequest):
        await send_note(chat["chat_id"], text, **kwargs)


@get_strings_dec("misc")
async def replymsg_setup_start(message, strings):
    with suppress(MessageNotModified):
        await message.edit_text(strings["send_text"])


async def replymsg_setup_finish(message, data):
    reply_text = await get_parsed_note_list(
        message, allow_reply_message=False, split_args=-1
    )
    return {"reply_text": reply_text}


@get_strings_dec("misc")
async def customise_reason_start(message: Message, strings: dict):
    await message.reply(strings["send_customised_reason"])


@get_strings_dec("misc")
async def customise_reason_finish(message: Message, _: dict, strings: dict):
    if message.text is None:
        await message.reply(strings["expected_text"])
        return False
    elif message.text in {"None"}:
        return {"reason": None}
    return {"reason": message.text}


__filters__ = {
    "delete_message": {
        "title": {"module": "misc", "string": "delmsg_filter_title"},
        "handle": delmsg_filter_handle,
        "del_btn_name": lambda msg, data: f"Del message: {data['handler']}",
    },
    "reply_message": {
        "title": {"module": "misc", "string": "replymsg_filter_title"},
        "handle": replymsg_filter_handler,
        "setup": {"start": replymsg_setup_start, "finish": replymsg_setup_finish},
        "del_btn_name": lambda msg, data: f"Reply to {data['handler']}: \"{data['reply_text'].get('text', 'None')}\" ",
    },
}
