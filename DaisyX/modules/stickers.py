# This file is part of DaisyXBot (Telegram Bot)

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

import datetime
import io
import math
import os
from io import BytesIO

import requests
from aiogram.types.input_file import InputFile
from bs4 import BeautifulSoup as bs
from PIL import Image
from telethon import *
from telethon.errors.rpcerrorlist import StickersetInvalidError
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import (
    DocumentAttributeSticker,
    InputStickerSetID,
    InputStickerSetShortName,
    MessageMediaPhoto,
)

from DaisyX import bot
from DaisyX.decorator import register
from DaisyX.services.events import register as Daisy
from DaisyX.services.telethon import tbot
from DaisyX.services.telethonuserbot import ubot

from .utils.disable import disableable_dec
from .utils.language import get_strings_dec


def is_it_animated_sticker(message):
    try:
        if message.media and message.media.document:
            mime_type = message.media.document.mime_type
            if "tgsticker" in mime_type:
                return True
            return False
        return False
    except BaseException:
        return False


def is_message_image(message):
    if message.media:
        if isinstance(message.media, MessageMediaPhoto):
            return True
        if message.media.document:
            if message.media.document.mime_type.split("/")[0] == "image":
                return True
        return False
    return False


async def silently_send_message(conv, text):
    await conv.send_message(text)
    response = await conv.get_response()
    await conv.mark_read(message=response)
    return response


async def stickerset_exists(conv, setname):
    try:
        await tbot(GetStickerSetRequest(InputStickerSetShortName(setname)))
        response = await silently_send_message(conv, "/addsticker")
        if response.text == "Invalid pack selected.":
            await silently_send_message(conv, "/cancel")
            return False
        await silently_send_message(conv, "/cancel")
        return True
    except StickersetInvalidError:
        return False


def resize_image(image, save_locaton):
    """Copyright Rhyse Simpson:
    https://github.com/skittles9823/SkittBot/blob/master/tg_bot/modules/stickers.py
    """
    im = Image.open(image)
    maxsize = (512, 512)
    if (im.width and im.height) < 512:
        size1 = im.width
        size2 = im.height
        if im.width > im.height:
            scale = 512 / size1
            size1new = 512
            size2new = size2 * scale
        else:
            scale = 512 / size2
            size1new = size1 * scale
            size2new = 512
        size1new = math.floor(size1new)
        size2new = math.floor(size2new)
        sizenew = (size1new, size2new)
        im = im.resize(sizenew)
    else:
        im.thumbnail(maxsize)
    im.save(save_locaton, "PNG")


def find_instance(items, class_or_tuple):
    for item in items:
        if isinstance(item, class_or_tuple):
            return item
    return None


@Daisy(pattern="^/searchsticker (.*)")
async def _(event):
    input_str = event.pattern_match.group(1)
    combot_stickers_url = "https://combot.org/telegram/stickers?q="
    text = requests.get(combot_stickers_url + input_str)
    soup = bs(text.text, "lxml")
    results = soup.find_all("a", {"class": "sticker-pack__btn"})
    titles = soup.find_all("div", "sticker-pack__title")
    if not results:
        await event.reply("No results found :(")
        return
    reply = f"Stickers Related to **{input_str}**:"
    for result, title in zip(results, titles):
        link = result["href"]
        reply += f"\nâ€¢ [{title.get_text()}]({link})"
    await event.reply(reply)


@Daisy(pattern="^/packinfo$")
async def _(event):
    approved_userss = approved_users.find({})
    for ch in approved_userss:
        iid = ch["id"]
        userss = ch["user"]
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return

    if not event.is_reply:
        await event.reply("Reply to any sticker to get it's pack info.")
        return
    rep_msg = await event.get_reply_message()
    if not rep_msg.document:
        await event.reply("Reply to any sticker to get it's pack info.")
        return
    stickerset_attr_s = rep_msg.document.attributes
    stickerset_attr = find_instance(stickerset_attr_s, DocumentAttributeSticker)
    if not stickerset_attr.stickerset:
        await event.reply("sticker does not belong to a pack.")
        return
    get_stickerset = await tbot(
        GetStickerSetRequest(
            InputStickerSetID(
                id=stickerset_attr.stickerset.id,
                access_hash=stickerset_attr.stickerset.access_hash,
            )
        )
    )
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)
    await event.reply(
        f"**Sticker Title:** `{get_stickerset.set.title}\n`"
        f"**Sticker Short Name:** `{get_stickerset.set.short_name}`\n"
        f"**Official:** `{get_stickerset.set.official}`\n"
        f"**Archived:** `{get_stickerset.set.archived}`\n"
        f"**Stickers In Pack:** `{len(get_stickerset.packs)}`\n"
        f"**Emojis In Pack:** {' '.join(pack_emojis)}"
    )


def find_instance(items, class_or_tuple):
    for item in items:
        if isinstance(item, class_or_tuple):
            return item
    return None


DEFAULTUSER = "DaisyX"
FILLED_UP_DADDY = "Invalid pack selected."


async def get_sticker_emoji(event):
    reply_message = await event.get_reply_message()
    try:
        final_emoji = reply_message.media.document.attributes[1].alt
    except:
        final_emoji = "😎"
    return final_emoji


@Daisy(pattern="^/kang ?(.*)")
async def _(event):
    if not event.is_reply:
        await event.reply("PLease, Reply To A Sticker / Image To Add It Your Pack")
        return
    reply_message = await event.get_reply_message()
    sticker_emoji = await get_sticker_emoji(event)
    input_str = event.pattern_match.group(1)
    if input_str:
        sticker_emoji = input_str
    user = await event.get_sender()
    if not user.first_name:
        user.first_name = user.id
    pack = 1
    userid = event.sender_id
    first_name = user.first_name
    packname = f"{first_name}'s Sticker Vol.{pack}"
    packshortname = f"DaisyX_stickers_{userid}"
    kanga = await event.reply("Hello, This Sticker Looks Noice. Mind if Daisy steal it")
    is_a_s = is_it_animated_sticker(reply_message)
    file_ext_ns_ion = "Stickers.png"
    file = await event.client.download_file(reply_message.media)
    uploaded_sticker = None
    if is_a_s:
        file_ext_ns_ion = "AnimatedSticker.tgs"
        uploaded_sticker = await ubot.upload_file(file, file_name=file_ext_ns_ion)
        packname = f"{first_name}'s Animated Sticker Vol.{pack}"
        packshortname = f"DaisyX_animated_{userid}"
    elif not is_message_image(reply_message):
        await kanga.edit("Oh no.. This Message type is invalid")
        return
    else:
        with BytesIO(file) as mem_file, BytesIO() as sticker:
            resize_image(mem_file, sticker)
            sticker.seek(0)
            uploaded_sticker = await ubot.upload_file(
                sticker, file_name=file_ext_ns_ion
            )

    await kanga.edit("This Sticker is Gonna Get Stolen.....")

    async with ubot.conversation("@Stickers") as d_conv:
        now = datetime.datetime.now()
        dt = now + datetime.timedelta(minutes=1)
        if not await stickerset_exists(d_conv, packshortname):

            await silently_send_message(d_conv, "/cancel")
            if is_a_s:
                response = await silently_send_message(d_conv, "/newanimated")
            else:
                response = await silently_send_message(d_conv, "/newpack")
            if "Yay!" not in response.text:
                await tbot.edit_message(
                    kanga, f"**Error**! @Stickers replied: {response.text}"
                )
                return
            response = await silently_send_message(d_conv, packname)
            if not response.text.startswith("Alright!"):
                await tbot.edit_message(
                    kanga, f"**Error**! @Stickers replied: {response.text}"
                )
                return
            w = await d_conv.send_file(
                file=uploaded_sticker, allow_cache=False, force_document=True
            )
            response = await d_conv.get_response()
            if "Sorry" in response.text:
                await tbot.edit_message(
                    kanga, f"**Error**! @Stickers replied: {response.text}"
                )
                return
            await silently_send_message(d_conv, sticker_emoji)
            await silently_send_message(d_conv, "/publish")
            response = await silently_send_message(d_conv, f"<{packname}>")
            await silently_send_message(d_conv, "/skip")
            response = await silently_send_message(d_conv, packshortname)
            if response.text == "Sorry, this short name is already taken.":
                await tbot.edit_message(
                    kanga, f"**Error**! @Stickers replied: {response.text}"
                )
                return
        else:
            await silently_send_message(d_conv, "/cancel")
            await silently_send_message(d_conv, "/addsticker")
            await silently_send_message(d_conv, packshortname)
            await d_conv.send_file(
                file=uploaded_sticker, allow_cache=False, force_document=True
            )
            response = await d_conv.get_response()
            if response.text == FILLED_UP_DADDY:
                while response.text == FILLED_UP_DADDY:
                    pack += 1
                    prevv = int(pack) - 1
                    packname = f"{first_name}'s Sticker Vol.{pack}"
                    packshortname = f"Vol_{pack}_with_{userid}"

                    if not await stickerset_exists(d_conv, packshortname):
                        await tbot.edit_message(
                            kanga,
                            "**Pack No. **"
                            + str(prevv)
                            + "** is full! Making a new Pack, Vol. **"
                            + str(pack),
                        )
                        if is_a_s:
                            response = await silently_send_message(
                                d_conv, "/newanimated"
                            )
                        else:
                            response = await silently_send_message(d_conv, "/newpack")
                        if "Yay!" not in response.text:
                            await tbot.edit_message(
                                kanga, f"**Error**! @Stickers replied: {response.text}"
                            )
                            return
                        response = await silently_send_message(d_conv, packname)
                        if not response.text.startswith("Alright!"):
                            await tbot.edit_message(
                                kanga, f"**Error**! @Stickers replied: {response.text}"
                            )
                            return
                        w = await d_conv.send_file(
                            file=uploaded_sticker,
                            allow_cache=False,
                            force_document=True,
                        )
                        response = await d_conv.get_response()
                        if "Sorry" in response.text:
                            await tbot.edit_message(
                                kanga, f"**Error**! @Stickers replied: {response.text}"
                            )
                            return
                        await silently_send_message(d_conv, sticker_emoji)
                        await silently_send_message(d_conv, "/publish")
                        response = await silently_send_message(
                            bot_conv, f"<{packname}>"
                        )
                        await silently_send_message(d_conv, "/skip")
                        response = await silently_send_message(d_conv, packshortname)
                        if response.text == "Sorry, this short name is already taken.":
                            await tbot.edit_message(
                                kanga, f"**Error**! @Stickers replied: {response.text}"
                            )
                            return
                    else:
                        await tbot.edit_message(
                            kanga,
                            "**Pack No. **"
                            + str(prevv)
                            + "** is full! Switching to Vol. **"
                            + str(pack),
                        )
                        await silently_send_message(d_conv, "/addsticker")
                        await silently_send_message(d_conv, packshortname)
                        await d_conv.send_file(
                            file=uploaded_sticker,
                            allow_cache=False,
                            force_document=True,
                        )
                        response = await d_conv.get_response()
                        if "Sorry" in response.text:
                            await tbot.edit_message(
                                kanga, f"**Error**! @Stickers replied: {response.text}"
                            )
                            return
                        await silently_send_message(d_conv, sticker_emoji)
                        await silently_send_message(d_conv, "/done")
            else:
                if "Sorry" in response.text:
                    await tbot.edit_message(
                        kanga, f"**Error**! @Stickers replied: {response.text}"
                    )
                    return
                await silently_send_message(d_conv, response)
                await silently_send_message(d_conv, sticker_emoji)
                await silently_send_message(d_conv, "/done")
    await kanga.edit("Inviting This Sticker To Your Pack 🚶")
    await kanga.edit(
        f"This Sticker Has Came To Your Pack.` \n**Check It Out** [Here](t.me/addstickers/{packshortname})"
    )
    os.system("rm -rf  Stickers.png")
    os.system("rm -rf  AnimatedSticker.tgs")
    os.system("rm -rf *.webp")


@register(cmds="getsticker")
@disableable_dec("getsticker")
@get_strings_dec("stickers")
async def get_sticker(message, strings):
    if "reply_to_message" not in message or "sticker" not in message.reply_to_message:
        await message.reply(strings["rpl_to_sticker"])
        return

    sticker = message.reply_to_message.sticker
    file_id = sticker.file_id
    text = strings["ur_sticker"].format(emoji=sticker.emoji, id=file_id)

    sticker_file = await bot.download_file_by_id(file_id, io.BytesIO())

    await message.reply_document(
        InputFile(
            sticker_file, filename=f"{sticker.set_name}_{sticker.file_id[:5]}.png"
        ),
        text,
    )


__mod_name__ = "Stickers"

__help__ = """
Stickers are the best way to show emotion.

<b>Available commands:</b>
- /search: Search stickers for given query.
- /packinfo: Reply to a sticker to get it's pack info
- /getsticker: Uploads the .png of the sticker you've replied to
- /kang <i>emoji for sticker</i>: Reply to Image / Sticker to Kang!
"""
