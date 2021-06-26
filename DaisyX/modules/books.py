# Copyright (C) 2020 DevsExpo
# Copyright (C) 2021 Inuka Asith
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


import os
import re

import requests
from bs4 import BeautifulSoup
from telethon import events

from DaisyX.services.telethon import tbot


@tbot.on(events.NewMessage(pattern="^/book (.*)"))
async def _(event):
    if event.fwd_from:
        return
    input_str = event.pattern_match.group(1)
    lool = 0
    KkK = await event.reply("searching for the book...")
    lin = "https://b-ok.cc/s/"
    text = input_str
    link = lin + text

    headers = [
        "User-Agent",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:74.0) Gecko/20100101 Firefox/74.0",
    ]
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    f = open("book.txt", "w")
    total = soup.find(class_="totalCounter")
    for nb in total.descendants:
        nbx = nb.replace("(", "").replace(")", "")
    if nbx == "0":
        await event.reply("No Books Found with that name.")
    else:

        for tr in soup.find_all("td"):
            for td in tr.find_all("h3"):
                for ts in td.find_all("a"):
                    title = ts.get_text()
                    lool = lool + 1
                for ts in td.find_all("a", attrs={"href": re.compile("^/book/")}):
                    ref = ts.get("href")
                    link = "https://b-ok.cc" + ref

                f.write("\n" + title)
                f.write("\nBook link:- " + link + "\n\n")

        f.write("By @DaisyXBot.")
        f.close()
        caption = "A collabration with Friday.\n Join Support @DaisySupport_Official"

        await tbot.send_file(
            event.chat_id,
            "book.txt",
            caption=f"**BOOKS GATHERED SUCCESSFULLY!\n\nBY DAISYX. JOIN THE SUPPORT @DaisySupport_Official.**",
        )
        os.remove("book.txt")
        await KkK.delete()
