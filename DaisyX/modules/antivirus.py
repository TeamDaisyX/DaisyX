#    MissJuliaRobot (A Telegram Bot Project)
#    Copyright (C) 2019-2021 Julia (https://t.me/MissJulia_Robot)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, in version 3 of the License.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see < https://www.gnu.org/licenses/agpl-3.0.en.html/ >.


import os

import cloudmersive_virus_api_client
from telethon.tl import functions, types
from telethon.tl.types import DocumentAttributeFilename, MessageMediaDocument

from DaisyX.config import get_str_key
from DaisyX.services.events import register
from DaisyX.services.telethon import tbot


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


VIRUS_API_KEY = get_str_key("VIRUS_API_KEY", required=False)
configuration = cloudmersive_virus_api_client.Configuration()
configuration.api_key["Apikey"] = VIRUS_API_KEY
api_instance = cloudmersive_virus_api_client.ScanApi(
    cloudmersive_virus_api_client.ApiClient(configuration)
)
allow_executables = True
allow_invalid_files = True
allow_scripts = True
allow_password_protected_files = True


@register(pattern="^/scanit$")
async def virusscan(event):
    if event.fwd_from:
        return
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        else:
            return
    if not event.reply_to_msg_id:
        await event.reply("Reply to a file to scan it.")
        return

    c = await event.get_reply_message()
    try:
        c.media.document
    except Exception:
        await event.reply("Thats not a file.")
        return
    h = c.media
    try:
        k = h.document.attributes
    except Exception:
        await event.reply("Thats not a file.")
        return
    if not isinstance(h, MessageMediaDocument):
        await event.reply("Thats not a file.")
        return
    if not isinstance(k[0], DocumentAttributeFilename):
        await event.reply("Thats not a file.")
        return
    try:
        virus = c.file.name
        await event.client.download_file(c, virus)
        gg = await event.reply("Scanning the file ...")
        fsize = c.file.size
        if not fsize <= 3145700:  # MAX = 3MB
            await gg.edit("File size exceeds 3MB")
            return
        api_response = api_instance.scan_file_advanced(
            c.file.name,
            allow_executables=allow_executables,
            allow_invalid_files=allow_invalid_files,
            allow_scripts=allow_scripts,
            allow_password_protected_files=allow_password_protected_files,
        )
        if api_response.clean_result is True:
            await gg.edit("This file is safe ✔️\nNo virus detected 🐞")
        else:
            await gg.edit("This file is Dangerous ☠️️\nVirus detected 🐞")
        os.remove(virus)
    except Exception as e:
        print(e)
        os.remove(virus)
        await gg.edit("Some error occurred.")
        return


__mod_name__ = "Virus Scan"
__help__ = """
 - /scanit: Scan a file for virus (MAX SIZE = 3MB)
 """
