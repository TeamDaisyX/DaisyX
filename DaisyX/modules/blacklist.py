#    MissJuliaRobot (A Telegram Bot Project)
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


import html

import tldextract
from telethon import events, types
from telethon.tl import functions

import DaisyX.services.sql.urlblacklist_sql as urlsql
from DaisyX.services.events import register
from DaisyX.services.telethon import tbot


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


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


@register(pattern="^/addurl")
async def _(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    if event.is_group:
        if await can_change_info(message=event):
            pass
        else:
            return
    chat = event.chat
    urls = event.text.split(None, 1)
    if len(urls) > 1:
        urls = urls[1]
        to_blacklist = list({uri.strip() for uri in urls.split("\n") if uri.strip()})
        blacklisted = []

        for uri in to_blacklist:
            extract_url = tldextract.extract(uri)
            if extract_url.domain and extract_url.suffix:
                blacklisted.append(extract_url.domain + "." + extract_url.suffix)
                urlsql.blacklist_url(
                    chat.id, extract_url.domain + "." + extract_url.suffix
                )

        if len(to_blacklist) == 1:
            extract_url = tldextract.extract(to_blacklist[0])
            if extract_url.domain and extract_url.suffix:
                await event.reply(
                    "Added <code>{}</code> domain to the blacklist!".format(
                        html.escape(extract_url.domain + "." + extract_url.suffix)
                    ),
                    parse_mode="html",
                )
            else:
                await event.reply("You are trying to blacklist an invalid url")
        else:
            await event.reply(
                "Added <code>{}</code> domains to the blacklist.".format(
                    len(blacklisted)
                ),
                parse_mode="html",
            )
    else:
        await event.reply("Tell me which urls you would like to add to the blacklist.")


@register(pattern="^/delurl")
async def _(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    if event.is_group:
        if await can_change_info(message=event):
            pass
        else:
            return
    chat = event.chat
    urls = event.text.split(None, 1)

    if len(urls) > 1:
        urls = urls[1]
        to_unblacklist = list({uri.strip() for uri in urls.split("\n") if uri.strip()})
        unblacklisted = 0
        for uri in to_unblacklist:
            extract_url = tldextract.extract(uri)
            success = urlsql.rm_url_from_blacklist(
                chat.id, extract_url.domain + "." + extract_url.suffix
            )
            if success:
                unblacklisted += 1

        if len(to_unblacklist) == 1:
            if unblacklisted:
                await event.reply(
                    "Removed <code>{}</code> from the blacklist!".format(
                        html.escape(to_unblacklist[0])
                    ),
                    parse_mode="html",
                )
            else:
                await event.reply("This isn't a blacklisted domain...!")
        elif unblacklisted == len(to_unblacklist):
            await event.reply(
                "Removed <code>{}</code> domains from the blacklist.".format(
                    unblacklisted
                ),
                parse_mode="html",
            )
        elif not unblacklisted:
            await event.reply("None of these domains exist, so they weren't removed.")
        else:
            await event.reply(
                "Removed <code>{}</code> domains from the blacklist. {} did not exist, so were not removed.".format(
                    unblacklisted, len(to_unblacklist) - unblacklisted
                ),
                parse_mode="html",
            )
    else:
        await event.reply(
            "Tell me which domains you would like to remove from the blacklist."
        )


@tbot.on(events.NewMessage(incoming=True))
async def on_url_message(event):
    if event.is_private:
        return
    chat = event.chat
    extracted_domains = []
    for (ent, txt) in event.get_entities_text():
        if ent.offset != 0:
            break
        if isinstance(ent, types.MessageEntityUrl):
            url = txt
            extract_url = tldextract.extract(url)
            extracted_domains.append(extract_url.domain + "." + extract_url.suffix)
    for url in urlsql.get_blacklisted_urls(chat.id):
        if url in extracted_domains:
            try:
                await event.delete()
            except:
                return


@register(pattern="^/geturl$")
async def _(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    if event.is_group:
        if await can_change_info(message=event):
            pass
        else:
            return
    chat = event.chat
    base_string = "Current <b>blacklisted</b> domains:\n"
    blacklisted = urlsql.get_blacklisted_urls(chat.id)
    if not blacklisted:
        await event.reply("There are no blacklisted domains here!")
        return
    for domain in blacklisted:
        base_string += "- <code>{}</code>\n".format(domain)
    await event.reply(base_string, parse_mode="html")


__help__ = """
<b> Daisy's filters are the blacklist too </b>
 - /addfilter [trigger] Select action: blacklists the trigger
 - /delfilter [trigger] : stop blacklisting a certain blacklist trigger
 - /filters: list all active blacklist filters
 
<b> Url Blacklist </B>
 - /geturl: View the current blacklisted urls
 - /addurl [urls]: Add a domain to the blacklist. The bot will automatically parse the url.
 - /delurl [urls]: Remove urls from the blacklist.
<b> Example:</b>
 - /addblacklist the admins suck: This will remove "the admins suck" everytime some non-admin types it
 - /addurl bit.ly: This would delete any message containing url "bit.ly"
"""
__mod_name__ = "Blacklist"
