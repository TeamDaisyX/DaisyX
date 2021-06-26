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

from asyncio import sleep
from datetime import datetime

import aiohttp
from pyrogram import filters
from pyrogram.errors import PeerIdInvalid

from DaisyX.services.pyrogram import pbot


class AioHttp:
    @staticmethod
    async def get_json(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.json()

    @staticmethod
    async def get_text(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.text()

    @staticmethod
    async def get_raw(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.read()


@pbot.on_message(filters.command("spwinfo") & ~filters.edited & ~filters.bot)
async def lookup(client, message):
    cmd = message.command
    if not message.reply_to_message and len(cmd) == 1:
        get_user = message.from_user.id
    elif len(cmd) == 1:
        if message.reply_to_message.forward_from:
            get_user = message.reply_to_message.forward_from.id
        else:
            get_user = message.reply_to_message.from_user.id
    elif len(cmd) > 1:
        get_user = cmd[1]
        try:
            get_user = int(cmd[1])
        except ValueError:
            pass
    try:
        user = await client.get_chat(get_user)
    except PeerIdInvalid:
        await message.reply_text("I don't know that User.")
        sleep(2)
        return
    url = f"https://api.intellivoid.net/spamprotection/v1/lookup?query={user.id}"
    a = await AioHttp().get_json(url)
    response = a["success"]
    if response is True:
        date = a["results"]["last_updated"]
        stats = f"**◢ Intellivoid• SpamProtection Info**:\n"
        stats += f' • **Updated on**: `{datetime.fromtimestamp(date).strftime("%Y-%m-%d %I:%M:%S %p")}`\n'
        stats += (
            f" • **Chat Info**: [Link](t.me/SpamProtectionBot/?start=00_{user.id})\n"
        )

        if a["results"]["attributes"]["is_potential_spammer"] is True:
            stats += f" • **User**: `USERxSPAM`\n"
        elif a["results"]["attributes"]["is_operator"] is True:
            stats += f" • **User**: `USERxOPERATOR`\n"
        elif a["results"]["attributes"]["is_agent"] is True:
            stats += f" • **User**: `USERxAGENT`\n"
        elif a["results"]["attributes"]["is_whitelisted"] is True:
            stats += f" • **User**: `USERxWHITELISTED`\n"

        stats += f' • **Type**: `{a["results"]["entity_type"]}`\n'
        stats += (
            f' • **Language**: `{a["results"]["language_prediction"]["language"]}`\n'
        )
        stats += f' • **Language Probability**: `{a["results"]["language_prediction"]["probability"]}`\n'
        stats += f"**Spam Prediction**:\n"
        stats += f' • **Ham Prediction**: `{a["results"]["spam_prediction"]["ham_prediction"]}`\n'
        stats += f' • **Spam Prediction**: `{a["results"]["spam_prediction"]["spam_prediction"]}`\n'
        stats += f'**Blacklisted**: `{a["results"]["attributes"]["is_blacklisted"]}`\n'
        if a["results"]["attributes"]["is_blacklisted"] is True:
            stats += (
                f' • **Reason**: `{a["results"]["attributes"]["blacklist_reason"]}`\n'
            )
            stats += f' • **Flag**: `{a["results"]["attributes"]["blacklist_flag"]}`\n'
        stats += f'**PTID**:\n`{a["results"]["private_telegram_id"]}`\n'
        await message.reply_text(stats, disable_web_page_preview=True)
    else:
        await message.reply_text("`Cannot reach SpamProtection API`")
        await sleep(3)
