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

import json

import aiohttp
from pyrogram import filters

from DaisyX.function.pluginhelpers import admins_only, get_text
from DaisyX.services.pyrogram import pbot


# Used my api key here, don't fuck with it
@pbot.on_message(
    filters.command("short") & ~filters.edited & ~filters.bot & ~filters.private
)
@admins_only
async def shortify(client, message):
    lel = await client.send_message(message.chat.id, "`Wait a sec....`")
    url = get_text(message)
    if "." not in url:
        await lel.edit("Defuq!. Is it a url?")
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
    await lel.edit(msg)
