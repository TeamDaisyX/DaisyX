#    Copyright (C) @chsaiujwal & InukaAsith 2020-2021
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import re
from datetime import datetime

import requests
from telethon import events

from DaisyX.function.telethonbasics import is_admin
from DaisyX.services.telethon import tbot


def main(url, filename):
    try:
        download_video("HD", url, filename)
    except (KeyboardInterrupt):
        download_video("SD", url, filename)


def download_video(quality, url, filename):
    html = requests.get(url).content.decode("utf-8")
    video_url = re.search(rf'{quality.lower()}_src:"(.+?)"', html).group(1)
    file_size_request = requests.get(video_url, stream=True)
    int(file_size_request.headers["Content-Length"])
    block_size = 1024
    with open(filename + ".mp4", "wb") as f:
        for data in file_size_request.iter_content(block_size):
            f.write(data)
    print("\nVideo downloaded successfully.")


@tbot.on(events.NewMessage(pattern="^/fbdl (.*)"))
async def _(event):
    if event.fwd_from:
        return
    if await is_admin(event, event.message.sender_id):
        url = event.pattern_match.group(1)
        x = re.match(r"^(https:|)[/][/]www.([^/]+[.])*facebook.com", url)

        if x:
            html = requests.get(url).content.decode("utf-8")
            await event.reply(
                "Starting Video download... \n Please note: FBDL is not for big files."
            )
        else:
            await event.reply(
                "This Video Is Either Private Or URL Is Invalid. Exiting... "
            )
            return

        _qualityhd = re.search('hd_src:"https', html)
        _qualitysd = re.search('sd_src:"https', html)
        _hd = re.search("hd_src:null", html)
        _sd = re.search("sd_src:null", html)

        list = []
        _thelist = [_qualityhd, _qualitysd, _hd, _sd]
        for id, val in enumerate(_thelist):
            if val != None:
                list.append(id)
        filename = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M-%S")

        main(url, filename)
        await event.reply("Video Downloaded Successfully. Starting To Upload.")

        kk = f"{filename}.mp4"
        caption = f"Facebook Video downloaded Successfully by @DaisyXBot.\nSay hi to devs @DaisySupport_Official."

        await tbot.send_file(
            event.chat_id,
            kk,
            caption="Facebook Video downloaded Successfully by @DaisyXBot.\nSay hi to devs @DaisySupport_Official.",
        )
        os.system(f"rm {kk}")
    else:
        await event.reply("`You Should Be Admin To Do This!`")
        return
