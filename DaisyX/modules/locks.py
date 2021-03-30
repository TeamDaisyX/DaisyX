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

from DaisyX.services.telethon import tbot
from telethon.errors import (
    ChatAdminRequiredError,
    ImageProcessFailedError,
    PhotoCropSizeSmallError,
)

from telethon.tl.functions.channels import EditAdminRequest, EditPhotoRequest

from telethon.tl.functions.messages import UpdatePinnedMessageRequest
from telethon.tl.types import (
    ChannelParticipantsAdmins,
    ChatAdminRights,
    ChatBannedRights,
    MessageEntityMentionName,
    MessageMediaPhoto,
)

from telethon import *
from telethon.tl import *
from telethon.errors import *

import os
from time import sleep
from telethon import events
from telethon.errors import FloodWaitError, ChatNotModifiedError
from telethon.errors import UserAdminInvalidError
from telethon.tl import functions
from telethon.tl import types
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import *

from DaisyX import *
from DaisyX.services.events import register

from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest

from telethon.errors.rpcerrorlist import MessageDeleteForbiddenError




"""
import itertools

from aiogram.types.chat_permissions import ChatPermissions

from DaisyX import bot
from DaisyX.decorator import register
from .utils.connections import chat_connection
from .utils.language import get_strings_dec


@register(cmds=["locks", "locktypes"], user_admin=True)
@chat_connection(only_groups=True)
@get_strings_dec('locks')
async def lock_types(message, chat, strings):
    chat_id = chat['chat_id']
    chat_title = chat['chat_title']
    text = strings['locks_header'].format(chat_title=chat_title)

    async for lock, status in lock_parser(chat_id):
        text += f"- {lock} = {status} \n"
    await message.reply(text)


@register(cmds="lock", user_can_restrict_members=True, bot_can_restrict_members=True)
@chat_connection(only_groups=True)
@get_strings_dec('locks')
async def lock_cmd(message, chat, strings):
    chat_id = chat['chat_id']
    chat_title = chat['chat_title']

    if (args := message.get_args().split(' ', 1)) == ['']:
        await message.reply(strings['no_lock_args'])
        return

    async for lock, status in lock_parser(chat_id, rev=True):
        if args[0] == lock[0]:
            if status is True:
                await message.reply(strings['already_locked'])
                continue

            to_lock = {lock[1]: False}
            new_perm = ChatPermissions(
                **to_lock
            )
            await bot.set_chat_permissions(chat_id, new_perm)
            await message.reply(strings['locked_successfully'].format(lock=lock[0], chat=chat_title))


@register(cmds="unlock", user_can_restrict_members=True, bot_can_restrict_members=True)
@chat_connection(only_groups=True)
@get_strings_dec('locks')
async def unlock_cmd(message, chat, strings):
    chat_id = chat['chat_id']
    chat_title = chat['chat_title']

    if (args := message.get_args().split(' ', 1)) == ['']:
        await message.reply(strings['no_unlock_args'])
        return

    async for lock, status in lock_parser(chat_id, rev=True):
        if args[0] == lock[0]:
            if status is False:
                await message.reply(strings['not_locked'])
                continue

            to_unlock = {lock[1]: True}
            new_perm = ChatPermissions(
                **to_unlock
            )
            await bot.set_chat_permissions(chat_id, new_perm)
            await message.reply(strings['unlocked_successfully'].format(lock=lock[0], chat=chat_title))


async def lock_parser(chat_id, rev=False):
    keywords = {
        'all': 'can_send_messages',
        'media': 'can_send_media_messages',
        'polls': 'can_send_polls',
        'others': 'can_send_other_messages'
    }
    current_lock = (await bot.get_chat(chat_id)).permissions

    for lock, keyword in itertools.zip_longest(dict(current_lock).keys(), keywords.items()):
        if keyword is not None and lock in keyword:
            if rev:
                lock = list([keyword[0], keyword[1]])
                status = not current_lock[keyword[1]]
            else:
                status = not current_lock[lock]
                lock = keyword[0]
            yield lock, status
"""            


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


@register(pattern="^/lock ?(.*)")
async def locks(event):
    if not event.is_group:
        return
    if event.is_group:
        if not await can_change_info(message=event):
            return
    input_str = event.pattern_match.group(1).lower()
    msg = None
    media = None
    sticker = None
    gif = None
    gamee = None
    ainline = None
    gpoll = None
    adduser = None
    cpin = None
    emlink = None
    changeinfo = None
    if input_str == "msg":
        msg = True
        what = "messages"
    elif input_str == "media":
        media = True
        what = "media"
    elif input_str == "sticker":
        sticker = True
        what = "stickers"
    elif input_str == "gif":
        gif = True
        what = "GIFs"
    elif input_str == "game":
        gamee = True
        what = "games"
    elif input_str == "inline":
        ainline = True
        what = "inline bots"
    elif input_str == "poll":
        gpoll = True
        what = "polls"
    elif input_str == "invite":
        adduser = True
        what = "invites"
    elif input_str == "pin":
        cpin = True
        what = "pins"
    elif input_str == "url":
        emlink = True
        what = "url links"
    elif input_str == "info":
        changeinfo = True
        what = "chat info"
    elif input_str == "all":
        msg = True
        media = True
        sticker = True
        gif = True
        gamee = True
        ainline = True
        emlink = True
        gpoll = True
        adduser = True
        cpin = True
        changeinfo = True
        what = "everything"
    else:
        if not input_str:
            await event.reply("I can't lock nothing !!")
            return
        await event.reply(f"Invalid lock type: {input_str}")
        return

    lock_rights = ChatBannedRights(
        until_date=None,
        send_messages=msg,
        send_media=media,
        send_stickers=sticker,
        send_gifs=gif,
        embed_links=emlink,
        send_games=gamee,
        send_inline=ainline,
        send_polls=gpoll,
        invite_users=adduser,
        pin_messages=cpin,
        change_info=changeinfo,
    )
    try:
        await tbot(
            EditChatDefaultBannedRightsRequest(event.chat_id, banned_rights=lock_rights)
        )
        await event.reply(f"Locked Successfully !")
    except Exception:
        await event.reply("Failed to lock.")
        return


@register(pattern="^/locktypes$")
async def ltypes(event):
    print("hi")
    if not event.is_group:
        return
    if event.is_group:
        if not await can_ban_users(message=event):
            return
    await event.reply(
        "**These are the valid lock types:**\n\nmsg\nmedia\nurl\nsticker\ngif\ngame\ninline\npoll\ninvite\npin\ninfo\nall"
    )

            
            
@register(pattern="^/locks$")
async def clocks(event):
    if not event.is_group:
        return
    if event.is_group:
        if not await can_ban_users(message=event):
            return
    try:
        c = event.chat.default_banned_rights
        await event.reply(str(c))
    except BaseException:
        return


__mod_name__ = "Locks"

__help__ = """
Use this feature to block users from sending specific message types to your group!

<b>Available commands are:</b>
- /locks or /locktypes: Use this command to know current state of your locks in your group!
- /lock (locktype): Locks a type of messages
- /unlock (locktype): Unlocks a type of message
"""
