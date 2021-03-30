from DaisyX import OWNER_ID
from DaisyX.services.telethon import tbot
from DaisyX import OPERATORS  as DEV_USERS
from DaisyX.services.events import register
import os
import asyncio
import os
import time
from datetime import datetime
from datetime import datetime
import asyncio

import os
import time
from datetime import datetime as dt
# from LEGEND import LEGENDX, telethn as client

TEMP_DOWNLOAD_DIRECTORY = "./"
path = "./"
opn = []

@register(pattern="/open")
async def _(event):
    xx = await event.reply("Processing...")
    if event.reply_to_msg_id:
        a = await event.get_reply_message()
        if a.media:
            b = await a.download_media()
            c = open(b, "r")
            d = c.read()
            c.close()
            n = 4096
            for bkl in range(0, len(d), n):
                opn.append(d[bkl : bkl + n])
            for bc in opn:
                await event.client.send_message(
                    event.chat_id,
                    f"{bc}",
                    reply_to=event.reply_to_msg_id,
                )
            await event.delete()
            opn.clear()
            os.remove(b)
            await xx.delete()
        else:
            return await event.reply("Reply to a readable file")
    else:
        return await event.reply("Reply to a readable file")
client = tbot
import time
from io import BytesIO
from pathlib import Path
from DaisyX.services.telethon import tbot as borg
from telethon import functions, types
from telethon.errors import PhotoInvalidDimensionsError
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.messages import SendMediaRequest
@register(pattern="^/dox ?(.*)")
async def get(event):
    name = event.text[5:]
    if name is None:
        await event.reply("reply to text message as `.ttf <file name>`")
        return
    m = await event.get_reply_message()
    if m.text:
        with open(name, "w") as f:
            f.write(m.message)
        await event.delete()
        await event.client.send_file(event.chat_id, name, force_document=True)
        os.remove(name)
    else:
        await event.reply("reply to text message as `.ttf <file name>`")

__help__ = """
 *You can make a file 
  name. *
 ✪ /dox tag a message <i>file name</i> example /dox example.py
 ✪ /open tag a file 
"""

__mod_name__ = "Core "
