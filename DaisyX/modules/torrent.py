# Copyright (C) 2021 TeamDaisyX


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

import requests
from telethon import *
from telethon import events
from telethon.tl import functions, types
from telethon.tl.types import *

from DaisyX.services.mongo import mongodb as db
from DaisyX.services.telethon import tbot

approved_users = db.approve


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerChat):
        ui = await tbot.get_peer_id(user)
        ps = (
            await tbot(functions.messages.GetFullChatRequest(chat.chat_id))
        ).full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    return False


@tbot.on(events.NewMessage(pattern="^/torrent (.*)"))
async def _(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id != iid or event.sender_id != userss:
            return
    sender = event.sender_id
    search = event.pattern_match.group(1)
    index = 0
    chatid = event.chat_id
    msg = await tbot.send_message(chatid, "Loading ...")
    msgid = msg.id
    await tbot.edit_message(
        chatid,
        msgid,
        "Daisy found some torrents for you. Take a look 👇",
        buttons=[
            [
                Button.inline(
                    "📤 Get Torrents from Sumanjay's API",
                    data=f"torrent-{sender}|{search}|{index}|{chatid}|{msgid}",
                )
            ],
            [
                Button.inline(
                    "❌ Cancel Search", data=f"torrentstop-{sender}|{chatid}|{msgid}"
                )
            ],
        ],
    )


@tbot.on(events.CallbackQuery(pattern=r"torrent(\-(.*))"))
async def paginate_news(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id != iid or event.sender_id != userss:
            return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, search, index, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if event.sender_id != sender:
        await event.answer("You haven't send that command !")
        return
    search = search.strip()
    index = int(index.strip())
    num = index
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    url = f"https://api.sumanjay.cf/torrent/?query={search}"
    try:
        results = requests.get(url).json()
    except Exception as e:
        await event.reply(
            "Sorry, either the server is down or no results found for your query."
        )
        print(e)
        return
    # print(results)
    age = results[num].get("age")
    leech = results[num].get("leecher")
    mag = results[num].get("magnet")
    name = results[num].get("name")
    seed = results[num].get("seeder")
    size = results[num].get("size")
    typ = results[num].get("type")
    header = f"**#{num} **"
    lastisthis = f"{header} **Name:** {name}\n**Uploaded:** {age} ago\n**Seeders:** {seed}\n**Leechers:** {leech}\n**Size:** {size}\n**Type:** {typ}\n**Magnet Link:** `{mag}`"
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.inline(
                    "◀️", data=f"prevtorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
                Button.inline("❌", data=f"torrentstop-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️", data=f"nexttorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁", data=f"newtorrent-{sender}|{search}|{chatid}|{msgid}"
                )
            ],
        ],
    )


@tbot.on(events.CallbackQuery(pattern=r"prevtorrent(\-(.*))"))
async def paginate_prevtorrent(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id != iid or event.sender_id != userss:
            return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, search, index, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if event.sender_id != sender:
        await event.answer("You haven't send that command !")
        return
    search = search.strip()
    index = int(index.strip())
    num = index - 1
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    url = f"https://api.sumanjay.cf/torrent/?query={search}"
    try:
        results = requests.get(url).json()
    except Exception as e:
        await event.reply("Sorry, Daisy Cant found any torrents for that word")
        print(e)
        return
    if num < 0:
        vector = len(results)
        num = vector - 1
    # print(results)
    age = results[int(num)].get("age")
    leech = results[int(num)].get("leecher")
    mag = results[int(num)].get("magnet")
    name = results[int(num)].get("name")
    seed = results[int(num)].get("seeder")
    size = results[int(num)].get("size")
    typ = results[int(num)].get("type")
    header = f"**#{num} **"
    lastisthis = f"{header} **Name:** {name}\n**Uploaded:** {age} ago\n**Seeders:** {seed}\n**Leechers:** {leech}\n**Size:** {size}\n**Type:** {typ}\n**Magnet Link:** `{mag}`"
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.inline(
                    "◀️", data=f"prevtorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
                Button.inline("❌", data=f"torrentstop-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️", data=f"nexttorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁", data=f"newtorrent-{sender}|{search}|{chatid}|{msgid}"
                )
            ],
        ],
    )


@tbot.on(events.CallbackQuery(pattern=r"nexttorrent(\-(.*))"))
async def paginate_nexttorrent(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id != iid or event.sender_id != userss:
            return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, search, index, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if event.sender_id != sender:
        await event.answer("You haven't send that command !")
        return
    search = search.strip()
    index = int(index.strip())
    num = index + 1
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    url = f"https://api.sumanjay.cf/torrent/?query={search}"
    try:
        results = requests.get(url).json()
    except Exception as e:
        await event.reply(
            "Sorry, either the server is down or no results found for your query."
        )
        print(e)
        return
    vector = len(results)
    if num > vector - 1:
        num = 0
    # print(results)
    age = results[int(num)].get("age")
    leech = results[int(num)].get("leecher")
    mag = results[int(num)].get("magnet")
    name = results[int(num)].get("name")
    seed = results[int(num)].get("seeder")
    size = results[int(num)].get("size")
    typ = results[int(num)].get("type")
    header = f"**#{num} **"
    lastisthis = f"{header} **Name:** {name}\n**Uploaded:** {age} ago\n**Seeders:** {seed}\n**Leechers:** {leech}\n**Size:** {size}\n**Type:** {typ}\n**Magnet Link:** `{mag}`"
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.inline(
                    "◀️", data=f"prevtorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
                Button.inline("❌", data=f"torrentstop-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️", data=f"nexttorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁", data=f"newtorrent-{sender}|{search}|{chatid}|{msgid}"
                )
            ],
        ],
    )


@tbot.on(events.CallbackQuery(pattern=r"torrentstop(\-(.*))"))
async def torrentstop(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id != iid or event.sender_id != userss:
            return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    if event.sender_id != sender:
        await event.answer("You haven't send that command !")
        return
    await tbot.edit_message(
        chatid,
        msgid,
        "Thanks for using.\n❤️ from [Daisy X](t.me/DaisyXBot) !",
        link_preview=False,
    )


@tbot.on(events.CallbackQuery(pattern=r"newtorrent(\-(.*))"))
async def paginate_nexttorrent(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.sender_id):
            pass
        elif event.chat_id != iid or event.sender_id != userss:
            return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, search, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if event.sender_id != sender:
        await event.answer("You haven't send that command !")
        return
    search = search.strip()
    num = 0
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    url = f"https://api.sumanjay.cf/torrent/?query={search}"
    try:
        results = requests.get(url).json()
    except Exception as e:
        await event.reply(
            "Sorry, either the server is down or no results found for your query."
        )
        print(e)
        return
    vector = len(results)
    if num > vector - 1:
        num = 0
    # print(results)
    age = results[num].get("age")
    leech = results[num].get("leecher")
    mag = results[num].get("magnet")
    name = results[num].get("name")
    seed = results[num].get("seeder")
    size = results[num].get("size")
    typ = results[num].get("type")
    header = f"**#{num} **"
    lastisthis = f"{header} **Name:** {name}\n**Uploaded:** {age} ago\n**Seeders:** {seed}\n**Leechers:** {leech}\n**Size:** {size}\n**Type:** {typ}\n**Magnet Link:** `{mag}`"
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.inline(
                    "◀️", data=f"prevtorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
                Button.inline("❌", data=f"torrentstop-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️", data=f"nexttorrent-{sender}|{search}|{num}|{chatid}|{msgid}"
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁", data=f"newtorrent-{sender}|{search}|{chatid}|{msgid}"
                )
            ],
        ],
    )


_help_ = """
 - /torrent <i>text</i>: Search for torrent links

Special Credits to Sumanjay for api and also for julia project
"""

_mod_name_ = "Torrent"
