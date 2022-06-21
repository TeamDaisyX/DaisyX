# Copyright (C) 2020-2021 by DevsExpo@Github, < https://github.com/DevsExpo >.
#
# This file is part of < https://github.com/DevsExpo/FridayUserBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/DevsExpo/blob/master/LICENSE >
#
# All rights reserved.

import os

import requests
from pyrogram import filters

from DaisyX.function.pluginhelpers import edit_or_reply, get_text
from DaisyX.services.pyrogram import pbot


@pbot.on_message(filters.command("paste") & ~filters.edited & ~filters.bot)
async def paste(client, message):
    pablo = await edit_or_reply(message, "`Please Wait.....`")
    tex_t = get_text(message)
    message_s = tex_t
    if not message_s:
        if not message.reply_to_message:
            await pablo.edit("`Reply To File / Give Me Text To Paste!`")
            return
        if not message.reply_to_message.text:
            file = await message.reply_to_message.download()
            m_list = open(file, "r").read()
            message_s = m_list
            print(message_s)
            os.remove(file)
        else:
            message_s = message.reply_to_message.text
    key = (
        requests.post("https://nekobin.com/api/documents", json={"content": message_s})
        .json()
        .get("result")
        .get("key")
    )
    url = f"https://nekobin.com/{key}"
    raw = f"https://nekobin.com/raw/{key}"
    reply_text = f"Pasted Text To [NekoBin]({url}) And For Raw [Click Here]({raw})"
    await pablo.edit(reply_text)
