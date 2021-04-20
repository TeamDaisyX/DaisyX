import json
import sys
from time import time

import aiohttp
from googletrans import Translator
from motor import version as mongover
from pykeyboard import InlineKeyboard
from pyrogram import __version__ as pyrover
from pyrogram.types import (
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
)
from Python_ARQ import ARQ
from search_engine_parser import GoogleSearch

from DaisyX import BOT_USERNAME, OWNER_ID
from DaisyX.function.pluginhelpers import convert_seconds_to_minutes as time_convert
from DaisyX.function.pluginhelpers import fetch
from DaisyX.services.pyrogram import pbot

SUDOERS = OWNER_ID
ARQ_API = "http://35.240.133.234:8000"
arq = ARQ(ARQ_API)

app = pbot
import socket


async def _netcat(host, port, content):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, int(port)))
    s.sendall(content.encode())
    s.shutdown(socket.SHUT_WR)
    while True:
        data = s.recv(4096).decode("utf-8").strip("\n\x00")
        if not data:
            break
        return data
    s.close()


async def paste(content):
    link = await _netcat("ezup.dev", 9999, content)
    return link


async def inline_help_func(__HELP__):
    buttons = InlineKeyboard(row_width=2)
    buttons.add(
        InlineKeyboardButton("Get More Help.", url=f"t.me/{BOT_USERNAME}?start=start"),
        InlineKeyboardButton("Go Inline!", switch_inline_query_current_chat=""),
    )
    answerss = [
        InlineQueryResultArticle(
            title="Inline Commands",
            description="Help Related To Inline Usage.",
            input_message_content=InputTextMessageContent(__HELP__),
            thumb_url="https://telegra.ph/file/109e8fe98acc6d262b7c6.jpg",
            reply_markup=buttons,
        )
    ]
    answerss = await alive_function(answerss)
    return answerss


async def alive_function(answers):
    buttons = InlineKeyboard(row_width=2)
    bot_state = "Dead" if not await app.get_me() else "Alive"
    # ubot_state = 'Dead' if not await app2.get_me() else 'Alive'
    buttons.add(
        InlineKeyboardButton("Main Bot", url="https://t.me/DaisyXbot"),
        InlineKeyboardButton("Go Inline!", switch_inline_query_current_chat=""),
    )

    msg = f"""
**[DaisyX✨](https://github.com/TeamDaisyX):**
**MainBot:** `{bot_state}`
**UserBot:** `Alive`
**Python:** `3.9`
**Pyrogram:** `{pyrover}`
**MongoDB:** `{mongover}`
**Platform:** `{sys.platform}`
**Profiles:** [BOT](t.me/{BOT_USERNAME}) | [UBOT](t.me/daisyxhelper)
"""
    answers.append(
        InlineQueryResultArticle(
            title="Alive",
            description="Check Bot's Stats",
            thumb_url="https://telegra.ph/file/debc179305d2e1f140636.jpg",
            input_message_content=InputTextMessageContent(
                msg, disable_web_page_preview=True
            ),
            reply_markup=buttons,
        )
    )
    return answers


async def translate_func(answers, lang, tex):
    i = Translator().translate(tex, dest=lang)
    msg = f"""
__**Translated to {lang}**__

**INPUT:**
{tex}

**OUTPUT:**
{i.text}"""
    answers.append(
        InlineQueryResultArticle(
            title=f"Translated to {lang}",
            description=i.text,
            input_message_content=InputTextMessageContent(msg),
        )
    )
    return answers


async def urban_func(answers, text):
    results = await arq.urbandict(text)
    for i in results:
        msg = f"""
**Query:** {text}

**Definition:** __{results[i].definition}__

**Example:** __{results[i].example}__"""

        answers.append(
            InlineQueryResultArticle(
                title=results[i].word,
                description=results[i].definition,
                input_message_content=InputTextMessageContent(msg),
            )
        )
    return answers


async def google_search_func(answers, text):
    gresults = await GoogleSearch().async_search(text)
    for i in gresults:
        try:
            msg = f"""
[{i['titles']}]({i['links']})
{i['descriptions']}"""

            answers.append(
                InlineQueryResultArticle(
                    title=i["titles"],
                    description=i["descriptions"],
                    input_message_content=InputTextMessageContent(
                        msg, disable_web_page_preview=True
                    ),
                )
            )
        except KeyError:
            pass
    return answers


async def wall_func(answers, text):
    results = await arq.wall(text)
    for i in results:
        try:
            answers.append(
                InlineQueryResultPhoto(
                    photo_url=results[i].url_image,
                    thumb_url=results[i].url_thumb,
                    caption=f"[Source]({results[i].url_image})",
                )
            )
        except KeyError:
            pass
    return answers


async def saavn_func(answers, text):
    buttons_list = []
    results = await arq.saavn(text)
    for i in results:
        buttons = InlineKeyboard(row_width=1)
        buttons.add(InlineKeyboardButton("Download | Play", url=results[i].media_url))
        buttons_list.append(buttons)
        duration = await time_convert(results[i].duration)
        caption = f"""
**Title:** {results[i].song}
**Album:** {results[i].album}
**Duration:** {duration}
**Release:** {results[i].year}
**Singers:** {results[i].singers}"""
        description = (
            f"{results[i].album} | {duration} "
            + f"| {results[i].singers} ({results[i].year})"
        )
        try:
            answers.append(
                InlineQueryResultArticle(
                    title=results[i].song,
                    input_message_content=InputTextMessageContent(
                        caption, disable_web_page_preview=True
                    ),
                    description=description,
                    thumb_url=results[i].image,
                    reply_markup=buttons_list[i],
                )
            )
        except (KeyError, ValueError):
            pass
    return answers


async def paste_func(answers, text):
    start_time = time()
    url = await paste(text)
    msg = f"__**{url}**__"
    end_time = time()
    answers.append(
        InlineQueryResultArticle(
            title=f"Pasted In {round(end_time - start_time)} Seconds.",
            description=url,
            input_message_content=InputTextMessageContent(msg),
        )
    )
    return answers


async def deezer_func(answers, text):
    buttons_list = []
    results = await arq.deezer(text, 5)
    for i in results:
        buttons = InlineKeyboard(row_width=1)
        buttons.add(InlineKeyboardButton("Download | Play", url=results[i].url))
        buttons_list.append(buttons)
        duration = await time_convert(results[i].duration)
        caption = f"""
**Title:** {results[i].title}
**Artist:** {results[i].artist}
**Duration:** {duration}
**Source:** [Deezer]({results[i].source})"""
        description = f"{results[i].artist} | {duration}"
        try:
            answers.append(
                InlineQueryResultArticle(
                    title=results[i].title,
                    thumb_url=results[i].thumbnail,
                    description=description,
                    input_message_content=InputTextMessageContent(
                        caption, disable_web_page_preview=True
                    ),
                    reply_markup=buttons_list[i],
                )
            )
        except (KeyError, ValueError):
            pass
    return answers


async def webss(url):
    start_time = time()
    if "." not in url:
        return
    screenshot = await fetch(f"https://patheticprogrammers.cf/ss?site={url}")
    end_time = time()
    # m = await app.send_photo(LOG_GROUP_ID, photo=screenshot["url"])
    await m.delete()
    a = []
    pic = InlineQueryResultPhoto(
        photo_url=screenshot["url"],
        caption=(f"`{url}`\n__Took {round(end_time - start_time)} Seconds.__"),
    )
    a.append(pic)
    return a


# Used my api key here, don't fuck with it
async def shortify(url):
    if "." not in url:
        return
    header = {
        "Authorization": "Bearer ad39983fa42d0b19e4534f33671629a4940298dc",
        "Content-Type": "application/json",
    }
    payload = {"long_url": f"{url}"}
    payload = json.dumps(payload)
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api-ssl.bitly.com/v4/shorten", headers=header, data=payload
        ) as resp:
            data = await resp.json()
    msg = f"**Original Url:** {url}\n**Shortened Url:** {data['link']}"
    a = []
    b = InlineQueryResultArticle(
        title="Link Shortened!",
        description=data["link"],
        input_message_content=InputTextMessageContent(
            msg, disable_web_page_preview=True
        ),
    )
    a.append(b)
    return a


async def torrent_func(answers, text):
    results = await arq.torrent(text)
    limit = 0
    for i in results:
        if limit > 48:
            break
        title = results[i].name
        size = results[i].size
        seeds = results[i].seeds
        leechs = results[i].leechs
        upload_date = results[i].uploaded + " Ago"
        magnet = results[i].magnet
        caption = f"""
**Title:** __{title}__
**Size:** __{size}__
**Seeds:** __{seeds}__
**Leechs:** __{leechs}__
**Uploaded:** __{upload_date}__
**Magnet:** __{magnet}__"""

        description = f"{size} | {upload_date} | Seeds: {seeds}"
        try:
            answers.append(
                InlineQueryResultArticle(
                    title=title,
                    description=description,
                    input_message_content=InputTextMessageContent(
                        caption, disable_web_page_preview=True
                    ),
                )
            )
            limit += 1
        except (KeyError, ValueError):
            pass
    return answers
