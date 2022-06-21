# Copyright (C) 2020-2021 by DevsExpo@Github, < https://github.com/DevsExpo >.
#
# This file is part of < https://github.com/DevsExpo/FridayUserBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/DevsExpo/blob/master/LICENSE >
#
# All rights reserved.

import asyncio

import feedparser
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import filters

from DaisyX.db.mongo_helpers.rss_db import (
    add_rss,
    basic_check,
    del_rss,
    delete_all,
    get_all,
    get_chat_rss,
    is_get_chat_rss,
    overall_check,
    update_rss,
)
from DaisyX.function.pluginhelpers import admins_only, edit_or_reply, get_text
from DaisyX.services.pyrogram import pbot


@pbot.on_message(filters.command("addrss") & ~filters.edited & ~filters.bot)
@admins_only
async def addrss(client, message):
    pablo = await edit_or_reply(message, "`Processing....`")
    lenk = get_text(message)
    if not lenk:
        await pablo.edit("Invalid Command Syntax, Please Check Help Menu To Know More!")
        return
    try:
        rss_d = feedparser.parse(lenk)
        rss_d.entries[0].title
    except:
        await pablo.edit(
            "ERROR: The link does not seem to be a RSS feed or is not supported"
        )
        return
    if lol := is_get_chat_rss(message.chat.id, lenk):
        await pablo.edit("This Link Already Added")
        return
    content = ""
    content += f"**{rss_d.entries[0].title}**"
    content += f"\n\n{rss_d.entries[0].link}"
    try:
        content += f"\n{rss_d.entries[0].description}"
    except:
        pass
    await client.send_message(message.chat.id, content)
    add_rss(message.chat.id, lenk, rss_d.entries[0].link)
    await pablo.edit("Successfully Added Link To RSS Watch")


@pbot.on_message(
    filters.command("testrss") & ~filters.edited & ~filters.bot & ~filters.private
)
@admins_only
async def testrss(client, message):
    pablo = await edit_or_reply(message, "`Processing....`")
    if damn := basic_check(message.chat.id):
        all = get_chat_rss(message.chat.id)
        for x in all:
            link = x.get("rss_link")
            rss_d = feedparser.parse(link)
            content = ""
            content += f"**{rss_d.entries[0].title}**"
            content += f"\n\nLink : {rss_d.entries[0].link}"
            try:
                content += f"\n{rss_d.entries[0].description}"
            except:
                pass
            await client.send_message(message.chat.id, content)
        await pablo.delete()
    else:
        rss_d = feedparser.parse("https://www.reddit.com/r/funny/new/.rss")
        Content = rss_d.entries[0]["title"] + "\n\n" + rss_d.entries[0]["link"]
        await client.send_message(message.chat.id, Content)
        await pablo.edit("This Chat Has No RSS So Sent Reddit RSS")


@pbot.on_message(
    filters.command("listrss") & ~filters.edited & ~filters.bot & ~filters.private
)
@admins_only
async def listrss(client, message):
    pablo = await edit_or_reply(message, "`Processing....`")
    damn = basic_check(message.chat.id)
    if not damn:
        await pablo.edit("This Chat Has No RSS!")
        return
    links = ""
    all = get_chat_rss(message.chat.id)
    for x in all:
        l = x.get("rss_link")
        links += f"{l}\n"
    content = f"Rss Found In The Chat Are : \n\n{links}"
    await client.send_message(message.chat.id, content)
    await pablo.delete()


@pbot.on_message(
    filters.command("delrss") & ~filters.edited & ~filters.bot & ~filters.private
)
@admins_only
async def delrss(client, message):
    pablo = await edit_or_reply(message, "`Processing....`")
    lenk = get_text(message)
    if not lenk:
        await pablo.edit("Invalid Command Syntax, Please Check Help Menu To Know More!")
        return
    lol = is_get_chat_rss(message.chat.id, lenk)
    if not lol:
        await pablo.edit("This Link Was Never Added")
        return
    del_rss(message.chat.id, lenk)
    await pablo.edit(f"Successfully Removed `{lenk}` From Chat RSS")


@pbot.on_message(
    filters.command("delallrss") & ~filters.edited & ~filters.bot & ~filters.private
)
@admins_only
async def delrss(client, message):
    pablo = await edit_or_reply(message, "`Processing....`")
    if not basic_check(message.chat.id):
        await pablo.edit("This Chat Has No RSS To Delete")
        return
    await delete_all()
    await pablo.edit("Successfully Deleted All RSS From The Chat")


async def check_rss():
    if not overall_check():
        return
    all = get_all()
    for one in all:
        link = one.get("rss_link")
        old = one.get("latest_rss")
        rss_d = feedparser.parse(link)
        if rss_d.entries[0].link != old:
            message = one.get("chat_id")
            content = ""
            content += f"**{rss_d.entries[0].title}**"
            content += f"\n\nLink : {rss_d.entries[0].link}"
            try:
                content += f"\n{rss_d.entries[0].description}"
            except:
                pass
            update_rss(message, link, rss_d.entries[0].link)
            try:
                await pbot.send_message(message, content)
                await asyncio.sleep(2)
            except:
                return


scheduler = AsyncIOScheduler()
scheduler.add_job(check_rss, "interval", minutes=10)
scheduler.start()

__mod_name__ = "RSS Feed"
__help__ = """
- /addrss : Add Rss to the chat
- /testrss : Test RSS Of The Chat
- /listrss : List all RSS Of The Chat
- /delrss : Delete RSS From The Chat
- /delallrss : Deletes All RSS From The Chat
"""
