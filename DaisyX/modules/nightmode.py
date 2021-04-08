#     (A Telegram Bot Project)
#    Copyright (C) 2019-Present Anonymous (https://t.me/MissJulia_Robot)

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, in version 3 of the License.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.

#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see < https://www.gnu.org/licenses/agpl-3.0.en.html >


from datetime import timedelta

import dateparser
from telethon import *
from telethon.tl.types import ChatBannedRights

from DaisyX.services.events import register
from DaisyX.services.mongo import mongodb as db
from DaisyX.services.telethon import tbot

nightmod = db.nightmode


closechat = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    send_polls=True,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)

openchat = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    send_polls=False,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)


async def can_change_info(message):
    result = await tbot(
        functions.channels.GetParticipantRequest(
            channel=message.chat_id,
            user_id=message.sender_id,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
        isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.change_info
    )


def get_info(id):
    return nightmod.find_one({"id": id})


@register(pattern="^/nightmode(?: |$)(.*)")
async def profanity(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    if MONGO_DB_URI is None:
        return
    if not await can_change_info(message=event):
        return
    input = event.pattern_match.group(1)
    chats = nightmod.find({})
    if not input:
        for c in chats:
            if event.chat_id == c["id"]:
                await event.reply(
                    "Please provide some input yes or no.\n\nCurrent setting is : **on**"
                )
                return
        await event.reply(
            "Please provide some input yes or no.\n\nCurrent setting is : **off**"
        )
        return
    if input == "on":
        if event.is_group:
            chats = nightmod.find({})
            for c in chats:
                if event.chat_id == c["id"]:
                    await event.reply("Nightmode is already activated for this chat.")
                    return
            nightmod.insert_one(
                {
                    "id": event.chat_id,
                    "valid": False,
                    "zone": None,
                    "ctime": None,
                    "otime": None,
                }
            )
            await event.reply(
                "Nightmode turned on for this chat\n**Note:** It will not work unless you specify time and zone with `/setnightmode`"
            )
    if input == "off":
        if event.is_group:
            chats = nightmod.find({})
            for c in chats:
                if event.chat_id == c["id"]:
                    nightmod.delete_one({"id": event.chat_id})
                    await event.reply("Nightmode turned off for this chat.")
                    return
        await event.reply("Nightmode isn't turned on for this chat.")
    if not input == "on" and not input == "off":
        await event.reply("I only understand by on or off")
        return


@register(pattern="^/setnightmode (.*)")
async def _(event):
    try:
        if event.fwd_from:
            return
        if event.is_private:
            return
        if MONGO_DB_URI is None:
            return
        if not await can_change_info(message=event):
            return
        quew = event.pattern_match.group(1)
        if "|" in quew:
            zone, ctime, otime = quew.split("|")
        zone = zone.strip()
        ctime = ctime.strip()
        otime = otime.strip()
        if len(ctime) != 11:
            await event.reply("Please enter valid date and time.")
            return
        if len(otime) != 11:
            await event.reply("Please enter valid date and time.")
            return
        if not zone and ctime and otime:
            await event.reply("Missing some parameters.")
            return
        ttime = dateparser.parse(
            "now", settings={"TIMEZONE": f"{zone}", "DATE_ORDER": "YMD"}
        )
        if ttime == None or otime == None or ctime == None:
            await event.reply("Please enter valid date and time and zone.")
            return
        cctime = dateparser.parse(
            f"{ctime}", settings={"TIMEZONE": f"{zone}", "DATE_ORDER": "DMY"}
        ) + timedelta(days=1)
        ootime = dateparser.parse(
            f"{otime}", settings={"TIMEZONE": f"{zone}", "DATE_ORDER": "DMY"}
        ) + timedelta(days=1)
        if cctime == ootime:
            await event.reply("Chat opening and closing time cannot be same.")
            return
        if not ootime > cctime and not cctime < ootime:
            await event.reply("Chat opening time must be greater than closing time")
            return
        if cctime > ootime:
            await event.reply("Chat closing time cant be greater than opening time")
            return
        # print (ttime)
        # print (cctime)
        # print (ootime)
        chats = nightmod.find({})
        for c in chats:
            if event.chat_id == c["id"] and c["valid"] == True:
                to_check = get_info(
                    id=event.chat_id,
                )
                nightmod.update_one(
                    {
                        "_id": to_check["_id"],
                        "id": to_check["id"],
                        "valid": to_check["valid"],
                        "zone": to_check["zone"],
                        "ctime": to_check["ctime"],
                        "otime": to_check["otime"],
                    },
                    {"$set": {"zone": zone, "ctime": cctime, "otime": ootime}},
                )
                await event.reply(
                    "Nightmode already set.\nI am updating the zone, closing time and opening time with the new zone, closing time and opening time."
                )
                return
        nightmod.insert_one(
            {
                "id": event.chat_id,
                "valid": True,
                "zone": zone,
                "ctime": cctime,
                "otime": ootime,
            }
        )
        await event.reply("Nightmode set successfully !")
    except Exception as e:
        print(e)


@tbot.on(events.NewMessage(pattern=None))
async def _(event):
    try:
        if event.is_private:
            return
        chats = nightmod.find({})
        for c in chats:
            # print(c)
            id = c["id"]
            valid = c["valid"]
            zone = c["zone"]
            ctime = c["ctime"]
            c["otime"]
            present = dateparser.parse(
                f"now", settings={"TIMEZONE": f"{zone}", "DATE_ORDER": "YMD"}
            )
            if present > ctime and valid:
                await tbot.send_message(
                    id,
                    f"**Nightbot:** It's time closing the chat now ...",
                )
                await tbot(
                    functions.messages.EditChatDefaultBannedRightsRequest(
                        peer=id, banned_rights=closechat
                    )
                )
                newtime = ctime + timedelta(days=1)
                to_check = get_info(id=id)
                if not to_check:
                    return
                print(newtime)
                print(to_check)
                nightmod.update_one(
                    {
                        "_id": to_check["_id"],
                        "id": to_check["id"],
                        "valid": to_check["valid"],
                        "zone": to_check["zone"],
                        "ctime": to_check["ctime"],
                        "otime": to_check["otime"],
                    },
                    {"$set": {"ctime": newtime}},
                )
                break
                return
            continue
    except Exception as e:
        print(e)


@tbot.on(events.NewMessage(pattern=None))
async def _(event):
    try:
        if event.is_private:
            return
        chats = nightmod.find({})
        for c in chats:
            # print(c)
            id = c["id"]
            valid = c["valid"]
            zone = c["zone"]
            c["ctime"]
            otime = c["otime"]
            present = dateparser.parse(
                f"now", settings={"TIMEZONE": f"{zone}", "DATE_ORDER": "YMD"}
            )
            if present > otime and valid:
                await tbot.send_message(
                    id,
                    f"**Nightbot:** It's time opening the chat now ...",
                )
                await tbot(
                    functions.messages.EditChatDefaultBannedRightsRequest(
                        peer=id, banned_rights=openchat
                    )
                )
                newtime = otime + timedelta(days=1)
                to_check = get_info(id=id)
                if not to_check:
                    return
                print(newtime)
                print(to_check)
                nightmod.update_one(
                    {
                        "_id": to_check["_id"],
                        "id": to_check["id"],
                        "valid": to_check["valid"],
                        "zone": to_check["zone"],
                        "ctime": to_check["ctime"],
                        "otime": to_check["otime"],
                    },
                    {"$set": {"otime": newtime}},
                )
                break
                return
            continue
    except Exception as e:
        print(e)


__help__ = """
Close your group at night
 - /nightmode [on/off]: turns on/off nightmode
 - /setnightmode [zone|closing time|opening time]: sets the time details
Syntax: /setnightmode America/New_York | 12:00:00 PM | 07:00:00 AM
"""

__mod_name__ = "Night Mode"
