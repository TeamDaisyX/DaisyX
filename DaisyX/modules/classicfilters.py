import asyncio
import os
import re

from telethon import Button, events, utils
from telethon.tl import functions, types

from DaisyX.services.events import register
from DaisyX.services.sql.filters_sql import (
    add_filter,
    get_all_filters,
    remove_all_filters,
    remove_filter,
)
from DaisyX.services.telethon import tbot

DELETE_TIMEOUT = 0
TYPE_TEXT = 0
TYPE_PHOTO = 1
TYPE_DOCUMENT = 2
last_triggered_filters = {}


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


@tbot.on(events.NewMessage(pattern=None))
async def on_snip(event):

    global last_triggered_filters

    name = event.raw_text

    if event.chat_id in last_triggered_filters:

        if name in last_triggered_filters[event.chat_id]:

            return False

    snips = get_all_filters(event.chat_id)

    if snips:

        for snip in snips:

            pattern = r"( |^|[^\w])" + re.escape(snip.keyword) + r"( |$|[^\w])"

            if re.search(pattern, name, flags=re.IGNORECASE):

                if snip.snip_type == TYPE_PHOTO:

                    media = types.InputPhoto(
                        int(snip.media_id),
                        int(snip.media_access_hash),
                        snip.media_file_reference,
                    )

                elif snip.snip_type == TYPE_DOCUMENT:

                    media = types.InputDocument(
                        int(snip.media_id),
                        int(snip.media_access_hash),
                        snip.media_file_reference,
                    )

                else:

                    media = None

                event.message.id

                if event.reply_to_msg_id:

                    event.reply_to_msg_id

                filter = ""
                options = ""
                butto = None

                if "|" in snip.reply:
                    filter, options = snip.reply.split("|")
                else:
                    filter = str(snip.reply)
                try:
                    filter = filter.strip()
                    button = options.strip()
                    if "•" in button:
                        mbutton = button.split("•")
                        lbutton = []
                        for i in mbutton:
                            params = re.findall(r"\'(.*?)\'", i) or re.findall(
                                r"\"(.*?)\"", i
                            )
                            lbutton.append(params)
                        longbutton = []
                        for c in lbutton:
                            butto = [Button.url(*c)]
                            longbutton.append(butto)
                    else:
                        params = re.findall(r"\'(.*?)\'", button) or re.findall(
                            r"\"(.*?)\"", button
                        )
                        butto = [Button.url(*params)]
                except BaseException:
                    filter = filter.strip()
                    butto = None

                try:
                    await event.reply(filter, buttons=longbutton, file=media)
                except:
                    await event.reply(filter, buttons=butto, file=media)

                if event.chat_id not in last_triggered_filters:

                    last_triggered_filters[event.chat_id] = []

                last_triggered_filters[event.chat_id].append(name)

                await asyncio.sleep(DELETE_TIMEOUT)

                last_triggered_filters[event.chat_id].remove(name)


@register(pattern="^/cfilter (.*)")
async def on_snip_save(event):
    if event.is_group:
        if not await can_change_info(message=event):
            return
    else:
        return

    name = event.pattern_match.group(1)
    msg = await event.get_reply_message()

    if msg:

        snip = {"type": TYPE_TEXT, "text": msg.message or ""}

        if msg.media:

            media = None

            if isinstance(msg.media, types.MessageMediaPhoto):

                media = utils.get_input_photo(msg.media.photo)

                snip["type"] = TYPE_PHOTO

            elif isinstance(msg.media, types.MessageMediaDocument):

                media = utils.get_input_document(msg.media.document)

                snip["type"] = TYPE_DOCUMENT

            if media:

                snip["id"] = media.id

                snip["hash"] = media.access_hash

                snip["fr"] = media.file_reference

        add_filter(
            event.chat_id,
            name,
            snip["text"],
            snip["type"],
            snip.get("id"),
            snip.get("hash"),
            snip.get("fr"),
        )

        await event.reply(
            f"Classic Filter {name} saved successfully. you can get it with {name}\nNote: Try our new filter system /addfilter "
        )

    else:

        await event.reply(
            "Usage: Reply to user message with /cfilter <text>.. \nNot Recomended use new filter system /savefilter"
        )


@register(pattern="^/stopcfilter (.*)")
async def on_snip_delete(event):
    if event.is_group:
        if not await can_change_info(message=event):
            return
    else:
        return
    name = event.pattern_match.group(1)

    remove_filter(event.chat_id, name)

    await event.reply(f"Filter **{name}** deleted successfully")


@register(pattern="^/cfilters$")
async def on_snip_list(event):
    if event.is_group:
        pass
    else:
        return
    all_snips = get_all_filters(event.chat_id)

    OUT_STR = "Available Classic Filters in the Current Chat:\n"

    if len(all_snips) > 0:

        for a_snip in all_snips:

            OUT_STR += f"👉{a_snip.keyword} \n"

    else:

        OUT_STR = "No Classic Filters in this chat. "

    if len(OUT_STR) > 4096:

        with io.BytesIO(str.encode(OUT_STR)) as out_file:

            out_file.name = "filters.text"

            await tbot.send_file(
                event.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption="Available Classic Filters in the Current Chat",
                reply_to=event,
            )

    else:

        await event.reply(OUT_STR)


@register(pattern="^/stopallcfilters$")
async def on_all_snip_delete(event):
    if event.is_group:
        if not await can_change_info(message=event):
            return
    else:
        return
    remove_all_filters(event.chat_id)
    await event.reply(f"Classic Filter in current chat deleted !")


file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")
