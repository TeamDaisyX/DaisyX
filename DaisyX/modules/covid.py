# Copyright (C) 2021 TheHamkerCat
# Edited by TeamDaisyX

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

from pyrogram import filters

from DaisyX.function.pluginhelpers import fetch, json_prettify
from DaisyX.services.pyrogram import pbot as app


@app.on_message(filters.command("covid") & ~filters.edited)
async def covid(_, message):
    if len(message.command) == 1:
        data = await fetch("https://corona.lmao.ninja/v2/all")
        data = await json_prettify(data)
        await app.send_message(message.chat.id, text=data)
        return
    country = message.text.split(None, 1)[1].strip()
    country = country.replace(" ", "")
    data = await fetch(f"https://corona.lmao.ninja/v2/countries/{country}")
    data = await json_prettify(data)
    await app.send_message(message.chat.id, text=data)
    return
