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



import time, markdown, base64, os
from datetime import datetime
from DaisyX import *
from DaisyX.services.events import register
from DaisyX.services.mongo import mongodb as db
from telethon import *
from telethon.tl import *
from telethon.tl.types import *
from telegraph import Telegraph
import requests
from DaisyX.Addons.tempmail.tempmail import TempMail
from DaisyX.services.telethon import tbot

tmail = db.tempmail
from DaisyX.config import get_str_key

TEMP_MAIL_KEY = get_str_key("APP_HASH", required=False)

tm = TempMail()
api_host = "privatix-temp-mail-v1.p.rapidapi.com"
api_key = TEMP_MAIL_KEY
tm.set_header(api_host, api_key)

def get_email(id):
    return tmail.find_one({"user": id})


def get_attachments(mail_id):
    url = f"https://privatix-temp-mail-v1.p.rapidapi.com/request/atchmnts/id/{mail_id}/"
    headers = {"x-rapidapi-key": TEMP_MAIL_KEY, "x-rapidapi-host": api_host}
    response = requests.request("GET", url, headers=headers)
    # print(response)
    return eval(response.text)


@register(pattern="^/newemail$")
async def _(event):
    try:
        if not event.is_private:
            await event.reply("You can only use this service in PM!")
            return
        sender = event.sender_id
        chatid = event.chat_id
        gmail = tmail.find({})
        for c in gmail:
            if event.sender_id == c["user"]:
                addr = get_email(event.sender_id)
                ttime = addr["time"]
                if not int(((datetime.now() - ttime)).total_seconds()) > 86400:  # 24 hrs
                    await event.reply(
                        "You have recently created a new email address, wait for 24hrs to change it"
                    )
                    return
                msg = await tbot.send_message(event.chat_id, "Working ...")
                msgid = msg.id
                await tbot.edit_message(
                    event.chat_id,
                    msgid,
                    "Are you sure you want to create a new email address ?\nYou will permanently lose your previous email address !",
                    buttons=[
                        [
                            Button.inline(
                                "Yes",
                                data=f"removeoldemail-{sender}|{chatid}|{msgid}",
                            )
                        ],
                        [
                            Button.inline(
                                "No",
                                data=f"dontremoveoldemail-{sender}|{chatid}|{msgid}",
                            )
                        ],
                    ],
                )
                return
        ttime = datetime.now()
        email = tm.get_email_address()
        hash = tm.get_hash(email)
        tmail.insert_one(
            {"user": event.sender_id, "time": ttime, "email": email, "hash": hash}
        )
        await event.reply(f"Your new temporary email is: {email}")
    except Exception as e:
        print(e)


@register(pattern="^/myemail$")
async def _(event):
    if not event.is_private:
        await event.reply("You can only use this service in PM!")
        return
    gmail = tmail.find({})
    for c in gmail:
        if event.sender_id == c["user"]:
            addr = get_email(event.sender_id)
            addrs = addr["email"]
            await event.reply(f"Your current email address is:\n{addrs}")
            return
    await event.reply(
        "You don't have any email address associated with your account, get one with /newmail"
    )


@register(pattern="^/checkinbox$")
async def _(event):
    try:
        if not event.is_private:
            await event.reply("You can only use this service in PM!")
            return
        gmail = tmail.find({})
        for c in gmail:
            if event.sender_id == c["user"]:
                addr = get_email(event.sender_id)
                email = addr["email"]
                hash = addr["hash"]
                sender = event.sender_id
                index = 0
                chatid = event.chat_id
                msg = await tbot.send_message(chatid, "Loading ...")
                msgid = msg.id
                await tbot.edit_message(
                    chatid,
                    msgid,
                    "Click on the below button to check your email inbox 👇",
                    buttons=[
                        [
                            Button.inline(
                                "▶️",
                                data=f"startcheckinbox-{sender}|{index}|{chatid}|{msgid}",
                            )
                        ],
                        [
                            Button.inline(
                                "❌", data=f"stopcheckinbox-{sender}|{chatid}|{msgid}"
                            )
                        ],
                    ],
                )
                return
        await event.reply(
            "You don't have any email address associated with your account, get one with /newmail"
        )
    except Exception as e:
        print(e)


@tbot.on(events.CallbackQuery(pattern=r"stopcheckinbox(\-(.*))"))
async def _(event):
    if not event.is_private:
        return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return
    await tbot.edit_message(chatid, msgid, "Thanks for using Julia ♥️")


@tbot.on(events.CallbackQuery(pattern=r"startcheckinbox(\-(.*))"))
async def _(event):
    if not event.is_private:
        return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, index, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return
    index = int(index.strip())
    num = index
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    to_check = get_email(event.sender_id)
    email = to_check["email"]
    hash = to_check["hash"]
    mails = tm.get_mailbox(email=email, email_hash=hash)
    if type(mails) is dict:
        for key, value in mails.items():
            if value == "There are no emails yet":
                await tbot.edit_message(chatid, msgid, "There are no emails yet.")
                return
    header = f"**#{num} **"
    from_mail = mails[int(num)]["mail_from"]
    subject = mails[int(num)]["mail_subject"]
    msg = mails[int(num)]["mail_text"]
    ttime = mails[int(num)]["mail_timestamp"]
    mail_id = mails[int(num)]["mail_id"]
    attch = int(mails[int(num)]["mail_attachments_count"])
    timestamp = ttime
    dt_object = datetime.fromtimestamp(timestamp)
    ttime = str(dt_object)

    telegraph = Telegraph()
    telegraph.create_account(short_name="MissJuliaRobot")
    if subject == "":
        subject = "No Subject"

    headers = f"**FROM**: {from_mail}\n**TO**: {email}\n**DATE**: {ttime}\n**MAIL BODY**:\n\n{msg}"
    nheaders = headers.replace("\n", "<br />")
    final = markdown.markdown(nheaders)
    response = telegraph.create_page(subject, html_content=final)

    tlink = "https://telegra.ph/{}".format(response["path"])

    if not attch > 0:
        lastisthis = (
            f"{header}MAIL FROM: {from_mail}"
            + "\n"
            + f"TO: {email}"
            + "\n"
            + f"DATE: `{ttime}`"
        )
    else:
        lastisthis = (
            f"{header}MAIL FROM: {from_mail}"
            + "\n"
            + f"TO: {email}"
            + "\n"
            + f"DATE: `{ttime}`"
            + "\n\n"
            + "**The attachments will be send to you shortly !**"
        )
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.url(
                    "Click here to read this mail",
                    url=f"{tlink}",
                ),
            ],
            [
                Button.inline(
                    "◀️",
                    data=f"checkinboxprev-{sender}|{num}|{chatid}|{msgid}",
                ),
                Button.inline("❌", data=f"stopcheckinbox-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️",
                    data=f"checkinboxnext-{sender}|{num}|{chatid}|{msgid}",
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁",
                    data=f"refreshinbox-{sender}|{chatid}|{msgid}",
                )
            ],
        ],
    )
    if attch > 0:
        gg = get_attachments(mail_id)
        for i in gg:
            fname = i["name"]
            with open(fname, "w+b") as f:
                f.write(base64.b64decode((i["content"]).encode()))
            await tbot.send_file(chatid, file=fname)
            os.remove(fname)


@tbot.on(events.CallbackQuery(pattern=r"checkinboxprev(\-(.*))"))
async def _(event):
    if not event.is_private:
        return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, index, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return

    index = int(index.strip())
    num = index - 1
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    to_check = get_email(event.sender_id)
    email = to_check["email"]
    hash = to_check["hash"]
    mails = tm.get_mailbox(email=email, email_hash=hash)
    if type(mails) is dict:
        for key, value in mails.items():
            if value == "There are no emails yet":
                await tbot.edit_message(chatid, msgid, "There are no emails yet.")
                return
    vector = len(mails)
    if num < 0:
        num = vector - 1
    # print(vector)
    # print(num)
    header = f"**#{num} **"
    from_mail = mails[int(num)]["mail_from"]
    subject = mails[int(num)]["mail_subject"]
    msg = mails[int(num)]["mail_text"]
    ttime = mails[int(num)]["mail_timestamp"]
    mail_id = mails[int(num)]["mail_id"]
    attch = int(mails[int(num)]["mail_attachments_count"])
    timestamp = ttime
    dt_object = datetime.fromtimestamp(timestamp)
    ttime = str(dt_object)

    header = f"**#{num} **"

    telegraph = Telegraph()
    telegraph.create_account(short_name="MissJuliaRobot")
    if subject == "":
        subject = "No Subject"

    headers = f"**FROM**: {from_mail}\n**TO**: {email}\n**DATE**: {ttime}\n**MAIL BODY**:\n\n{msg}"
    nheaders = headers.replace("\n", "<br />")
    final = markdown.markdown(nheaders)
    response = telegraph.create_page(subject, html_content=final)

    tlink = "https://telegra.ph/{}".format(response["path"])
    if not attch > 0:
        lastisthis = (
            f"{header}MAIL FROM: {from_mail}"
            + "\n"
            + f"TO: {email}"
            + "\n"
            + f"DATE: `{ttime}`"
        )
    else:
        lastisthis = (
            f"{header}MAIL FROM: {from_mail}"
            + "\n"
            + f"TO: {email}"
            + "\n"
            + f"DATE: `{ttime}`"
            + "\n\n"
            + "**The attachments will be send to you shortly !**"
        )
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.url(
                    "Click here to read this mail",
                    url=f"{tlink}",
                ),
            ],
            [
                Button.inline(
                    "◀️",
                    data=f"checkinboxprev-{sender}|{num}|{chatid}|{msgid}",
                ),
                Button.inline("❌", data=f"stopcheckinbox-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️",
                    data=f"checkinboxnext-{sender}|{num}|{chatid}|{msgid}",
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁",
                    data=f"refreshinbox-{sender}|{chatid}|{msgid}",
                )
            ],
        ],
    )
    if attch > 0:
        gg = get_attachments(mail_id)
        for i in gg:
            fname = i["name"]
            with open(fname, "w+b") as f:
                f.write(base64.b64decode((i["content"]).encode()))
            await tbot.send_file(chatid, file=fname)
            os.remove(fname)


@tbot.on(events.CallbackQuery(pattern=r"checkinboxnext(\-(.*))"))
async def _(event):
    if not event.is_private:
        return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, index, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return

    index = int(index.strip())
    num = index + 1
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    to_check = get_email(event.sender_id)
    email = to_check["email"]
    hash = to_check["hash"]
    mails = tm.get_mailbox(email=email, email_hash=hash)
    if type(mails) is dict:
        for key, value in mails.items():
            if value == "There are no emails yet":
                await tbot.edit_message(chatid, msgid, "There are no emails yet.")
                return
    vector = len(mails)
    if num > vector - 1:
        num = 0
    # print(vector)
    # print(num)
    header = f"**#{num} **"
    from_mail = mails[int(num)]["mail_from"]
    subject = mails[int(num)]["mail_subject"]
    msg = mails[int(num)]["mail_text"]
    ttime = mails[int(num)]["mail_timestamp"]
    mail_id = mails[int(num)]["mail_id"]
    attch = int(mails[int(num)]["mail_attachments_count"])
    timestamp = ttime
    dt_object = datetime.fromtimestamp(timestamp)
    ttime = str(dt_object)

    header = f"**#{num} **"

    telegraph = Telegraph()
    telegraph.create_account(short_name="MissJuliaRobot")
    if subject == "":
        subject = "No Subject"

    headers = f"**FROM**: {from_mail}\n**TO**: {email}\n**DATE**: {ttime}\n**MAIL BODY**:\n\n{msg}"
    nheaders = headers.replace("\n", "<br />")
    final = markdown.markdown(nheaders)
    response = telegraph.create_page(subject, html_content=final)

    tlink = "https://telegra.ph/{}".format(response["path"])
    if not attch > 0:
        lastisthis = (
            f"{header}MAIL FROM: {from_mail}"
            + "\n"
            + f"TO: {email}"
            + "\n"
            + f"DATE: `{ttime}`"
        )
    else:
        lastisthis = (
            f"{header}MAIL FROM: {from_mail}"
            + "\n"
            + f"TO: {email}"
            + "\n"
            + f"DATE: `{ttime}`"
            + "\n\n"
            + "**The attachments will be send to you shortly !**"
        )
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.url(
                    "Click here to read this mail",
                    url=f"{tlink}",
                ),
            ],
            [
                Button.inline(
                    "◀️",
                    data=f"checkinboxprev-{sender}|{num}|{chatid}|{msgid}",
                ),
                Button.inline("❌", data=f"stopcheckinbox-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️",
                    data=f"checkinboxnext-{sender}|{num}|{chatid}|{msgid}",
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁",
                    data=f"refreshinbox-{sender}|{chatid}|{msgid}",
                )
            ],
        ],
    )
    if attch > 0:
        gg = get_attachments(mail_id)
        for i in gg:
            fname = i["name"]
            with open(fname, "w+b") as f:
                f.write(base64.b64decode((i["content"]).encode()))
            await tbot.send_file(chatid, file=fname)
            os.remove(fname)


@tbot.on(events.CallbackQuery(pattern=r"refreshinbox(\-(.*))"))
async def _(event):
    if not event.is_private:
        return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return

    num = 0
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    to_check = get_email(event.sender_id)
    email = to_check["email"]
    hash = to_check["hash"]
    mails = tm.get_mailbox(email=email, email_hash=hash)
    if type(mails) is dict:
        for key, value in mails.items():
            if value == "There are no emails yet":
                await tbot.edit_message(chatid, msgid, "There are no emails yet.")
                return
    vector = len(mails)
    if num > vector - 1:
        num = 0
    # print(vector)
    # print(num)
    header = f"**#{num} **"
    from_mail = mails[int(num)]["mail_from"]
    subject = mails[int(num)]["mail_subject"]
    msg = mails[int(num)]["mail_text"]
    ttime = mails[int(num)]["mail_timestamp"]
    mail_id = mails[int(num)]["mail_id"]
    attch = int(mails[int(num)]["mail_attachments_count"])
    timestamp = ttime
    dt_object = datetime.fromtimestamp(timestamp)
    ttime = str(dt_object)

    header = f"**#{num} **"

    telegraph = Telegraph()
    telegraph.create_account(short_name="MissJuliaRobot")
    if subject == "":
        subject = "No Subject"

    headers = f"**FROM**: {from_mail}\n**TO**: {email}\n**DATE**: {ttime}\n**MAIL BODY**:\n\n{msg}"
    nheaders = headers.replace("\n", "<br />")
    final = markdown.markdown(nheaders)
    response = telegraph.create_page(subject, html_content=final)

    tlink = "https://telegra.ph/{}".format(response["path"])
    if not attch > 0:
        lastisthis = (
            f"{header}MAIL FROM: {from_mail}"
            + "\n"
            + f"TO: {email}"
            + "\n"
            + f"DATE: `{ttime}`"
        )
    else:
        lastisthis = (
            f"{header}MAIL FROM: {from_mail}"
            + "\n"
            + f"TO: {email}"
            + "\n"
            + f"DATE: `{ttime}`"
            + "\n\n"
            + "**The attachments will be send to you shortly !**"
        )
    await tbot.edit_message(
        chatid,
        msgid,
        lastisthis,
        link_preview=False,
        buttons=[
            [
                Button.url(
                    "Click here to read this mail",
                    url=f"{tlink}",
                ),
            ],
            [
                Button.inline(
                    "◀️",
                    data=f"checkinboxprev-{sender}|{num}|{chatid}|{msgid}",
                ),
                Button.inline("❌", data=f"stopcheckinbox-{sender}|{chatid}|{msgid}"),
                Button.inline(
                    "▶️",
                    data=f"checkinboxnext-{sender}|{num}|{chatid}|{msgid}",
                ),
            ],
            [
                Button.inline(
                    "Refresh 🔁",
                    data=f"refreshinbox-{sender}|{chatid}|{msgid}",
                )
            ],
        ],
    )
    if attch > 0:
        gg = get_attachments(mail_id)
        for i in gg:
            fname = i["name"]
            with open(fname, "w+b") as f:
                f.write(base64.b64decode((i["content"]).encode()))
            await tbot.send_file(chatid, file=fname)
            os.remove(fname)


@tbot.on(events.CallbackQuery(pattern=r"stopcheckinbox(\-(.*))"))
async def _(event):
    if not event.is_private:
        return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return
    await tbot.edit_message(chatid, msgid, "Thanks for using Julia ♥️")


@tbot.on(events.CallbackQuery(pattern=r"dontremoveoldemail(\-(.*))"))
async def _(event):
    if not event.is_private:
        return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return
    await tbot.edit_message(chatid, msgid, "Okay !\nNot a problem 😉")


@tbot.on(events.CallbackQuery(pattern=r"removeoldemail(\-(.*))"))
async def _(event):
    if not event.is_private:
        return
    tata = event.pattern_match.group(1)
    data = tata.decode()
    meta = data.split("-", 1)[1]
    # print(meta)
    if "|" in meta:
        sender, chatid, msgid = meta.split("|")
    sender = int(sender.strip())
    chatid = int(chatid.strip())
    msgid = int(msgid.strip())
    if not event.sender_id == sender:
        await event.answer("You haven't send that command !")
        return
    ttime = datetime.now()
    email = tm.get_email_address()
    hash = tm.get_hash(email)
    to_check = get_email(id=sender)
    tmail.update_one(
        {
            "_id": to_check["_id"],
            "user": to_check["user"],
            "time": to_check["time"],
            "email": to_check["email"],
            "hash": to_check["hash"],
        },
        {"$set": {"time": ttime, "email": email, "hash": hash}},
    )
    await tbot.edit_message(chatid, msgid, f"Your new temporary email is: {email}")

    
__mod_name__ = "Temp mail"
__help__ ="""
 - /newemail: Registers your account for a new email address
 - /myemail: Gives your current email address
 - /checkinbox: Checks the inbox associated with the account for new emails
**NOTE**: Emails received are temporary and they will be deleted after 60 minutes of arrival
"""
