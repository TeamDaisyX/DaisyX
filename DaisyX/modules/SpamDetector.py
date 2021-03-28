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


from DaisyX.services.telethon import tbot
from datetime import datetime
from DaisyX import OWNER_ID
from telethon import events, types
import asyncio
from DaisyX.services.mongo import mongodb as db
global spamcounter
spamcounter = 0

def get_time(id):
    spammers = db.leecher
    return spammers.find_one({"id": id})

@tbot.on(events.NewMessage(pattern=None))
async def spammers(event):
    if str(event.sender_id) in str(OWNER_ID):
        return
    global spamcounter
    starttimer = datetime.now()
    spamcounter += 1
    sender = event.sender_id
    senderr = await event.get_sender()
    check = sender
    msg = event.text
    USERSPAM = []
    USERSPAM.append(check)
    USERSPAM.append(msg)

    for (ent, txt) in event.get_entities_text():
        if isinstance(ent, types.MessageEntityBotCommand):
            pass
        else:
            return

    if (
        spamcounter > 10
        and event.sender_id == USERSPAM[0]
        and ((datetime.now() - starttimer)).seconds <= 3
    ) or (
        spamcounter > 10 and event.sender_id == USERSPAM[0] and event.text == USERSPAM[1]
    ):
        spamcounter = 0
        if senderr.username is None:
            st = senderr.first_name
            hh = senderr.id
            final = f"[{st}](tg://user?id={hh}) you are detected as a spammer according to my algorithms.\nYou will be restricted from using any bot commands for 24 hours !"
        else:
            st = senderr.username
            final = f"@{st} you are detected as a spammer according to my algorithms.\nYou will be restricted from using any bot commands for 24 hours !"
            pass
    else:
        return
    spammers = db.leecher

    users = spammers.find({})
    for c in users:
        if USERSPAM[0] == c["id"]:
            print("spammers never die")
            return
    spammers.insert_one({"id": USERSPAM[0], "time": datetime.now()})
    if event.is_group:
       msg = await event.respond(final)
       await asyncio.sleep(10)
       await msg.delete()
    else:
       await event.respond(final)

@tbot.on(events.NewMessage(pattern=None))
async def spammers(event):]
    spammers = db.leecher
    users = spammers.find({})
    for c in users:
        if event.sender_id == c["id"]:
            to_check = get_time(id=event.sender_id)
            ttime = to_check["time"]
            if (datetime.now() - ttime).seconds > 86400:
                spammers.delete_one({"id": event.sender_id})
            else:
                return
