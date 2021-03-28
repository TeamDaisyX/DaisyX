import os
#import ffmpeg
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.raw.functions.channels import GetFullChannel
from DaisyX.function.pluginhelpers import fetch_audio, get_readable_time, progress,edit_or_reply,admins_only
from DaisyX.services.pyrogram import pbot
import asyncio
import math
import os
import random
import string
import requests
import time
from pyrogram import filters
from json import JSONDecodeError
import json
@pbot.on_message(filters.command(["identify", "shazam"]))
@admins_only
async def shazamm(client, message):
    kek = await edit_or_reply(message, "`Shazaming In Progress!`")
    if not message.reply_to_message:
        await kek.edit("Reply To The Audio.")
        return
    if os.path.exists("friday.mp3"):
      os.remove("friday.mp3")
    kkk = await fetch_audio(client, message)
    downloaded_file_name = kkk
    f = {"file": (downloaded_file_name, open(downloaded_file_name, "rb"))}
    await kek.edit("**Searching For This Song In Friday's DataBase.**")
    r = requests.post("https://starkapi.herokuapp.com/shazam/", files = f)
    try:
      xo = r.json()
    except JSONDecodeError:
      await kek.edit('`Seems Like Our Server Has Some Issues, Please Try Again Later!`')
      return
    if xo.get("success") is False:
        await kek.edit("`Song Not Found IN Database. Please Try Again.`")
        os.remove(downloaded_file_name)
        return
    xoo = xo.get("response")
    zz = xoo[1]
    zzz = zz.get("track")
    Col = zzz.get("sections")[3]
    nt = zzz.get("images")	
    image = nt.get("coverarthq")
    by = zzz.get("subtitle")
    title = zzz.get("title")
    messageo = f"""<b>Song Shazamed.</b>
<b>Song Name : </b>{title}
<b>Song By : </b>{by}
<u><b>Identified Using @DaisyXBot - Join our support @DaisySupport_Official</b></u>
<i>Powered by @FridayOT</i>
"""
    await client.send_photo(message.chat.id, image, messageo, parse_mode="HTML")
    os.remove(downloaded_file_name)
    await kek.delete()

#__mod_name__ = "Shazam"
#__help__ = """
#<b> SHAZAMMER </b>
#<u> Find any song with it's music or part of song</u>
#- /shazam : identify the song from Friday's Database

#<i> Special credits to friday userbot</i>
#"""
