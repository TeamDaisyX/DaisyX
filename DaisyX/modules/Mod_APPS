# Copyright (C) 2020-2021 by DevsExpo@Github, < https://github.com/DevsExpo >.
#
# This file is part of < https://github.com/DevsExpo/FridayUserBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/DevsExpo/blob/master/LICENSE >
#
# All rights reserved.


import os
import re
import time

import requests
import wget
from bs4 import BeautifulSoup
from pyrogram import filters

from DaisyX.function.pluginhelpers import admins_only, progress
from DaisyX.services.pyrogram import pbot


@pbot.on_message(filters.command("mod") & ~filters.edited & ~filters.bot)
@admins_only
async def mudapk(client, message):
    pablo = await client.send_message(message.chat.id, "`Searching For Mod App.....`")
    sgname = message.text
    if not sgname:
        await pablo.edit("Invalid Command Syntax, Please Check Help Menu To Know More!")
        return
    PabloEscobar = (
        f"https://an1.com/tags/MOD/?story={sgname}&do=search&subaction=search"
    )
    r = requests.get(PabloEscobar)
    soup = BeautifulSoup(r.content, "html5lib")
    mydivs = soup.find_all("div", {"class": "search-results"})
    Pop = soup.find_all("div", {"class": "title"})
    sucker = mydivs[0]
    pH9 = sucker.find("a").contents[0]
    file_name = pH9

    pH = sucker.findAll("img")
    imme = wget.download(pH[0]["src"])
    Pablo = Pop[0].a["href"]

    ro = requests.get(Pablo)
    soup = BeautifulSoup(ro.content, "html5lib")

    mydis = soup.find_all("a", {"class": "get-product"})

    Lol = mydis[0]

    lemk = "https://an1.com" + Lol["href"]

    rr = requests.get(lemk)
    soup = BeautifulSoup(rr.content, "html5lib")

    script = soup.find("script", type="text/javascript")

    leek = re.search(r'href=[\'"]?([^\'" >]+)', script.text).group()
    dl_link = leek[5:]

    r = requests.get(dl_link)
    await pablo.edit("Downloading Mod App")
    open(f"{file_name}.apk", "wb").write(r.content)
    c_time = time.time()
    await pablo.edit(f"`Downloaded {file_name}! Now Uploading APK...`")
    await client.send_document(
        message.chat.id,
        document=open(f"{file_name}.apk", "rb"),
        thumb=imme,
        progress=progress,
        progress_args=(
            pablo,
            c_time,
            f"`Uploading {file_name} Mod App`",
            f"{file_name}.apk",
        ),
    )
    os.remove(f"{file_name}.apk")
    os.remove(imme)
    await pablo.delete()


# __mod_name__ = "Mod Apps"
# __help__ = """
# - /mod [app name] : Download and upload mod apps
# """
