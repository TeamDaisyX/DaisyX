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

import asyncio

from pyrogram import filters
from pyrogram.errors import RPCError

from DaisyX import BOT_ID
from DaisyX.db.mongo_helpers.lockurl import add_chat, get_session, remove_chat
from DaisyX.function.pluginhelpers import (
    admins_only,
    edit_or_reply,
    get_url,
    member_permissions,
)
from DaisyX.services.pyrogram import pbot


@pbot.on_message(
    filters.command("urllock") & ~filters.edited & ~filters.bot & ~filters.private
)
@admins_only
async def hmm(_, message):
    global daisy_chats
    try:
        user_id = message.from_user.id
    except:
        return
    if "can_change_info" not in await member_permissions(
        message.chat.id, user_id
    ):
        await message.reply_text("**You don't have enough permissions**")
        return
    if len(message.command) != 2:
        await message.reply_text(
            "I only recognize `/urllock on` and /urllock `off only`"
        )
        return
    status = message.text.split(None, 1)[1]
    message.chat.id
    if status in ["ON", "on", "On"]:
        lel = await edit_or_reply(message, "`Processing...`")
        lol = add_chat(int(message.chat.id))
        if not lol:
            await lel.edit("URL Block Already Activated In This Chat")
            return
        await lel.edit(
            f"URL Block Successfully Added For Users In The Chat {message.chat.id}"
        )

    elif status in ["OFF", "off", "Off"]:
        lel = await edit_or_reply(message, "`Processing...`")
        Escobar = remove_chat(int(message.chat.id))
        if not Escobar:
            await lel.edit("URL Block Was Not Activated In This Chat")
            return
        await lel.edit(
            f"URL Block Successfully Deactivated For Users In The Chat {message.chat.id}"
        )
    else:
        await message.reply_text(
            "I only recognize `/urllock on` and /urllock `off only`"
        )


@pbot.on_message(
    filters.incoming & filters.text & ~filters.private & ~filters.channel & ~filters.bot
)
async def hi(client, message):
    if not get_session(int(message.chat.id)):
        message.continue_propagation()
    try:
        user_id = message.from_user.id
    except:
        return
    try:
        if len(await member_permissions(message.chat.id, user_id)) >= 1:
            message.continue_propagation()
        if len(await member_permissions(message.chat.id, BOT_ID)) < 1:
            message.continue_propagation()
        if "can_delete_messages" not in await member_permissions(
            message.chat.id, BOT_ID
        ):
            message.continue_propagation()
    except RPCError:
        return
    try:

        lel = get_url(message)
    except:
        return

    if lel:
        try:
            await message.delete()
            sender = message.from_user.mention()
            lol = await client.send_message(
                message.chat.id,
                f"{sender}, Your message was deleted as it contain a link(s). \n ❗️ Links are not allowed here",
            )
            await asyncio.sleep(10)
            await lol.delete()
        except:
            message.continue_propagation()
    else:
        message.continue_propagation()
