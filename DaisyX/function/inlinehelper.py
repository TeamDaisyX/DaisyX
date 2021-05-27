import json
import sys
from random import randint
from time import time

import aiohttp
from aiohttp import ClientSession
from googletrans import Translator
from motor import version as mongover
from pykeyboard import InlineKeyboard
from pyrogram import __version__ as pyrover
from pyrogram.raw.functions import Ping
from pyrogram.types import (
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InlineQueryResultPhoto,
    InputTextMessageContent,
)
from Python_ARQ import ARQ
from search_engine_parser import GoogleSearch

from DaisyX import BOT_USERNAME, OWNER_ID
from DaisyX.config import get_str_key
from DaisyX.function.pluginhelpers import convert_seconds_to_minutes as time_convert
from DaisyX.function.pluginhelpers import fetch
from DaisyX.services.pyrogram import pbot

ARQ_API = get_str_key("ARQ_API", required=True)
ARQ_API_KEY = ARQ_API
SUDOERS = OWNER_ID
ARQ_API_URL = "https://thearq.tech"

# Aiohttp Client
print("[INFO]: INITIALZING AIOHTTP SESSION")
aiohttpsession = ClientSession()
# ARQ Client
print("[INFO]: INITIALIZING ARQ CLIENT")
arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)

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


async def translate_func(answers, lang, tex):
    i = Translator().translate(tex, dest=lang)
    msg = f"""
__**Translated from {i.src} to {lang}**__

**INPUT:**
{tex}

**OUTPUT:**
{i.text}"""
    answers.extend(
        [
            InlineQueryResultArticle(
                title=f"Translated from {i.src} to {lang}.",
                description=i.text,
                input_message_content=InputTextMessageContent(msg),
            ),
            InlineQueryResultArticle(
                title=i.text, input_message_content=InputTextMessageContent(i.text)
            ),
        ]
    )
    return answers


async def urban_func(answers, text):
    results = await arq.urbandict(text)
    if not results.ok:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=results.result,
                input_message_content=InputTextMessageContent(results.result),
            )
        )
        return answers
    results = results.result
    limit = 0
    for i in results:
        if limit > 48:
            break
        limit += 1
        msg = f"""
**Query:** {text}

**Definition:** __{i.definition}__

**Example:** __{i.example}__"""

        answers.append(
            InlineQueryResultArticle(
                title=i.word,
                description=i.definition,
                input_message_content=InputTextMessageContent(msg),
            )
        )
    return answers


async def google_search_func(answers, text):
    gresults = await GoogleSearch().async_search(text)
    limit = 0
    for i in gresults:
        if limit > 48:
            break
        limit += 1

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
    if not results.ok:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=results.result,
                input_message_content=InputTextMessageContent(results.result),
            )
        )
        return answers
    limit = 0
    results = results.result
    for i in results:
        if limit > 48:
            break
        limit += 1
        answers.append(
            InlineQueryResultPhoto(
                photo_url=i.url_image,
                thumb_url=i.url_thumb,
                caption=f"[Source]({i.url_image})",
            )
        )
    return answers


async def saavn_func(answers, text):
    buttons_list = []
    results = await arq.saavn(text)
    if not results.ok:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=results.result,
                input_message_content=InputTextMessageContent(results.result),
            )
        )
        return answers
    results = results.result
    for count, i in enumerate(results):
        buttons = InlineKeyboard(row_width=1)
        buttons.add(InlineKeyboardButton("Download | Play", url=i.media_url))
        buttons_list.append(buttons)
        duration = await time_convert(i.duration)
        caption = f"""
**Title:** {i.song}
**Album:** {i.album}
**Duration:** {duration}
**Release:** {i.year}
**Singers:** {i.singers}"""
        description = f"{i.album} | {duration} " + f"| {i.singers} ({i.year})"
        answers.append(
            InlineQueryResultArticle(
                title=i.song,
                input_message_content=InputTextMessageContent(
                    caption, disable_web_page_preview=True
                ),
                description=description,
                thumb_url=i.image,
                reply_markup=buttons_list[count],
            )
        )
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
    if not results.ok:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=results.result,
                input_message_content=InputTextMessageContent(results.result),
            )
        )
        return answers
    results = results.result
    for count, i in enumerate(results):
        buttons = InlineKeyboard(row_width=1)
        buttons.add(InlineKeyboardButton("Download | Play", url=i.url))
        buttons_list.append(buttons)
        duration = await time_convert(i.duration)
        caption = f"""
**Title:** {i.title}
**Artist:** {i.artist}
**Duration:** {duration}
**Source:** [Deezer]({i.source})"""
        description = f"{i.artist} | {duration}"
        answers.append(
            InlineQueryResultArticle(
                title=i.title,
                thumb_url=i.thumbnail,
                description=description,
                input_message_content=InputTextMessageContent(
                    caption, disable_web_page_preview=True
                ),
                reply_markup=buttons_list[count],
            )
        )
    return answers


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
    msg = data["link"]
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
    if not results.ok:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=results.result,
                input_message_content=InputTextMessageContent(results.result),
            )
        )
        return answers
    limit = 0
    results = results.result
    for i in results:
        if limit > 48:
            break
        title = i.name
        size = i.size
        seeds = i.seeds
        leechs = i.leechs
        upload_date = i.uploaded + " Ago"
        magnet = i.magnet
        caption = f"""
**Title:** __{title}__
**Size:** __{size}__
**Seeds:** __{seeds}__
**Leechs:** __{leechs}__
**Uploaded:** __{upload_date}__
**Magnet:** `{magnet}`"""

        description = f"{size} | {upload_date} | Seeds: {seeds}"
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
    return answers


async def wiki_func(answers, text):
    data = await arq.wiki(text)
    if not data.ok:
        answers.append(
            InlineQueryResultArticle(
                title="Error",
                description=data.result,
                input_message_content=InputTextMessageContent(data.result),
            )
        )
        return answers
    data = data.result
    msg = f"""
**QUERY:**
{data.title}

**ANSWER:**
__{data.answer}__"""
    answers.append(
        InlineQueryResultArticle(
            title=data.title,
            description=data.answer,
            input_message_content=InputTextMessageContent(msg),
        )
    )
    return answers


async def ping_func(answers):
    t1 = time()
    ping = Ping(ping_id=randint(696969, 6969696))
    await app.send(ping)
    t2 = time()
    ping = f"{str(round((t2 - t1), 2))} Seconds"
    answers.append(
        InlineQueryResultArticle(
            title=ping, input_message_content=InputTextMessageContent(f"__**{ping}**__")
        )
    )
    return answers


async def pokedexinfo(answers, pokemon):
    Pokemon = f"https://some-random-api.ml/pokedex?pokemon={pokemon}"
    result = await fetch(Pokemon)
    buttons = InlineKeyboard(row_width=1)
    buttons.add(
        InlineKeyboardButton("Pokedex", switch_inline_query_current_chat="pokedex")
    )
    caption = f"""
**Pokemon:** `{result['name']}`
**Pokedex:** `{result['id']}`
**Type:** `{result['type']}`
**Abilities:** `{result['abilities']}`
**Height:** `{result['height']}`
**Weight:** `{result['weight']}`
**Gender:** `{result['gender']}`
**Stats:** `{result['stats']}`
**Description:** `{result['description']}`"""
    answers.append(
        InlineQueryResultPhoto(
            photo_url=f"https://img.pokemondb.net/artwork/large/{pokemon}.jpg",
            title=result["name"],
            description=result["description"],
            caption=caption,
            reply_markup=buttons,
        )
    )
    return answers
