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

# =================== CONSTANT ===================
PP_TOO_SMOL = "The image is too small"
PP_ERROR = "Failure while processing image"
NO_ADMIN = "I am not an admin"
NO_PERM = "I don't have sufficient permissions!"

CHAT_PP_CHANGED = "Chat Picture Changed"
CHAT_PP_ERROR = (
    "Some issue with updating the pic,"
    "maybe you aren't an admin,"
    "or don't have the desired rights."
)
INVALID_MEDIA = "Invalid Extension"


BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

KICK_RIGHTS = ChatBannedRights(until_date=None, view_messages=True)

MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)

UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)


# ================================================


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


async def can_promote_users(message):
    result = await tbot(
        functions.channels.GetParticipantRequest(
            channel=message.chat_id,
            user_id=message.sender_id,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
        isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.ban_users
    )


async def can_ban_users(message):
    result = await tbot(
        functions.channels.GetParticipantRequest(
            channel=message.chat_id,
            user_id=message.sender_id,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
        isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.ban_users
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


async def can_del(message):
    result = await tbot(
        functions.channels.GetParticipantRequest(
            channel=message.chat_id,
            user_id=message.sender_id,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
        isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.delete_messages
    )


async def can_pin_msg(message):
    result = await tbot(
        functions.channels.GetParticipantRequest(
            channel=message.chat_id,
            user_id=message.sender_id,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
        isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.pin_messages
    )


async def get_user_sender_id(user, event):
    if isinstance(user, str):
        user = int(user)

    try:
        user_obj = await tbot.get_entity(user)
    except (TypeError, ValueError) as err:
        await event.edit(str(err))
        return None

    return user_obj


async def get_user_from_event(event):
    """ Get the user from argument or replied message. """
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_obj = await tbot.get_entity(previous_message.sender_id)
    else:
        user = event.pattern_match.group(1)

        if user.isnumeric():
            user = int(user)

        if not user:
            await event.reply("Pass the user's username, id or reply!")
            return

        try:
            user_obj = await tbot.get_entity(user)
        except (TypeError, ValueError) as err:
            await event.reply(str(err))
            return None

    return user_obj


def find_instance(items, class_or_tuple):
    for item in items:
        if isinstance(item, class_or_tuple):
            return item
    return None


@register(pattern="^/setgrouppic$")
async def set_group_photo(gpic):
    replymsg = await gpic.get_reply_message()
    chat = await gpic.get_chat()
    photo = None

    if gpic.is_group:
        if not await can_change_info(message=gpic):
            return
    else:
        return

    if replymsg and replymsg.media:
        if isinstance(replymsg.media, MessageMediaPhoto):
            photo = await tbot.download_media(message=replymsg.photo)
        elif "image" in replymsg.media.document.mime_type.split("/"):
            photo = await tbot.download_file(replymsg.media.document)
        else:
            await gpic.reply(INVALID_MEDIA)

    if photo:
        try:
            await tbot(EditPhotoRequest(gpic.chat_id, await tbot.upload_file(photo)))
            await gpic.reply(CHAT_PP_CHANGED)

        except PhotoCropSizeSmallError:
            await gpic.reply(PP_TOO_SMOL)
        except ImageProcessFailedError:
            await gpic.reply(PP_ERROR)
        except:
            await gpic.reply("Failed to set group pic.")


@register(pattern="^/settitle ?(.*)")
async def settitle(promt):
    textt = promt.pattern_match.group(1)
    thatuser = textt.split(" ")[0]
    title_admin = textt.split(" ")[1]
    # print(thatuser)
    # print(title_admin)
    if thatuser:
        user = await tbot.get_entity(thatuser)
    else:
        await promt.reply("Pass the user's username or id or followed by title !")
        return

    if promt.is_group:
        if not await can_promote_users(message=promt):
            return
    else:
        return

    if promt.is_group:
        if not await is_register_admin(promt.input_chat, user.id):
            await promt.reply("How can i set title of a non-admin ?")
            return
        pass

    try:
        result = await tbot(
            functions.channels.GetParticipantRequest(
                channel=promt.chat_id,
                user_id=user.id,
            )
        )
        p = result.participant

        await tbot(
            EditAdminRequest(
                promt.chat_id,
                user_id=user.id,
                admin_rights=p.admin_rights,
                rank=title_admin,
            )
        )

        await promt.reply("Title set successfully !")

    except Exception:
        await promt.reply("Failed to set title.")
        return


@register(pattern="^/users$")
async def get_users(show):
    if not show.is_group:
        return
    if show.is_group:
        if not await is_register_admin(show.input_chat, show.sender_id):
            return
    info = await tbot.get_entity(show.chat_id)
    title = info.title if info.title else "this chat"
    mentions = "Users in {}: \n".format(title)
    async for user in tbot.iter_participants(show.chat_id):
        if not user.deleted:
            mentions += f"\n[{user.first_name}](tg://user?id={user.id}) {user.id}"
        else:
            mentions += f"\nDeleted Account {user.id}"
    file = open("userslist.txt", "w+")
    file.write(mentions)
    file.close()
    await tbot.send_file(
        show.chat_id,
        "userslist.txt",
        caption="Users in {}".format(title),
        reply_to=show.id,
    )
    os.remove("userslist.txt")


@register(pattern="^/zombies(?: |$)(.*)")
async def rm_deletedacc(show):
    """ For .delusers command, list all the ghost/deleted accounts in a chat. """
    con = show.pattern_match.group(1).lower()
    del_u = 0
    del_status = "`No deleted accounts found, Group is cleaned as Hell`"

    if not show.is_group:
        return

    if show.is_group:
        if not await can_ban_users(message=show):
            return

    # Here laying the sanity check
    chat = await show.get_chat()
    admin = chat.admin_rights.ban_users
    creator = chat.creator

    # Well
    if not admin and not creator:
        await show.reply("`I don't have enough permissions!`")
        return

    if con != "clean":
        await show.reply("`Searching for zombie accounts...`")
        async for user in tbot.iter_participants(show.chat_id):
            if user.deleted:
                del_u += 1

        if del_u > 0:
            del_status = f"Found **{del_u}** deleted account(s) in this group,\
            \nclean them by using `/zombies clean`"

        await show.reply(del_status)
        return

    await show.reply("`Deleting deleted accounts...`")
    del_u = 0
    del_a = 0

    async for user in tbot.iter_participants(show.chat_id):
        if user.deleted:
            try:
                await tbot(EditBannedRequest(show.chat_id, user.id, BANNED_RIGHTS))
            except ChatAdminRequiredError:
                await show.reply("`I don't have ban rights in this group`")
                return
            except UserAdminInvalidError:
                del_u -= 1
                del_a += 1
            await tbot(EditBannedRequest(show.chat_id, user.id, UNBAN_RIGHTS))
            del_u += 1

    if del_u > 0:
        del_status = f"Cleaned **{del_u}** deleted account(s)"

    if del_a > 0:
        del_status = f"Cleaned **{del_u}** deleted account(s) \
        \n**{del_a}** deleted admin accounts are not removed"

    await show.reply(del_status)


@register(pattern="^/kickthefools$")
async def _(event):
    if event.fwd_from:
        return

    if event.is_group:
        if not await can_ban_users(message=event):
            return
    else:
        return

    # Here laying the sanity check
    chat = await event.get_chat()
    admin = chat.admin_rights.ban_users
    creator = chat.creator

    # Well
    if not admin and not creator:
        await event.reply("`I don't have enough permissions!`")
        return

    c = 0
    KICK_RIGHTS = ChatBannedRights(until_date=None, view_messages=True)
    done = await event.reply("Working ...")
    async for i in tbot.iter_participants(event.chat_id):

        if isinstance(i.status, UserStatusLastMonth):
            status = await tbot(EditBannedRequest(event.chat_id, i, KICK_RIGHTS))
            if not status:
                return
            c = c + 1

        if isinstance(i.status, UserStatusLastWeek):
            status = await tbot(EditBannedRequest(event.chat_id, i, KICK_RIGHTS))
            if not status:
                return
            c = c + 1

    if c == 0:
        await done.edit("Got no one to kick 😔")
        return

    required_string = "Successfully Kicked **{}** users"
    await event.reply(required_string.format(c))


@register(pattern="^/unbanall$")
async def _(event):
    if not event.is_group:
        return

    if event.is_group:
        if not await can_ban_users(message=event):
            return

    # Here laying the sanity check
    chat = await event.get_chat()
    admin = chat.admin_rights.ban_users
    creator = chat.creator

    # Well
    if not admin and not creator:
        await event.reply("`I don't have enough permissions!`")
        return

    done = await event.reply("Searching Participant Lists.")
    p = 0
    async for i in tbot.iter_participants(
        event.chat_id, filter=ChannelParticipantsKicked, aggressive=True
    ):
        rights = ChatBannedRights(until_date=0, view_messages=False)
        try:
            await tbot(functions.channels.EditBannedRequest(event.chat_id, i, rights))
        except FloodWaitError as ex:
            logger.warn("sleeping for {} seconds".format(ex.seconds))
            sleep(ex.seconds)
        except Exception as ex:
            await event.reply(str(ex))
        else:
            p += 1

    if p == 0:
        await done.edit("No one is banned in this chat")
        return
    required_string = "Successfully unbanned **{}** users"
    await event.reply(required_string.format(p))


@register(pattern="^/unmuteall$")
async def _(event):
    if not event.is_group:
        return
    if event.is_group:
        if not await can_ban_users(message=event):
            return

    # Here laying the sanity check
    chat = await event.get_chat()
    admin = chat.admin_rights.ban_users
    creator = chat.creator

    # Well
    if not admin and not creator:
        await event.reply("`I don't have enough permissions!`")
        return

    done = await event.reply("Working ...")
    p = 0
    async for i in tbot.iter_participants(
        event.chat_id, filter=ChannelParticipantsBanned, aggressive=True
    ):
        rights = ChatBannedRights(
            until_date=0,
            send_messages=False,
        )
        try:
            await tbot(functions.channels.EditBannedRequest(event.chat_id, i, rights))
        except FloodWaitError as ex:
            logger.warn("sleeping for {} seconds".format(ex.seconds))
            sleep(ex.seconds)
        except Exception as ex:
            await event.reply(str(ex))
        else:
            p += 1

    if p == 0:
        await done.edit("No one is muted in this chat")
        return
    required_string = "Successfully unmuted **{}** users"
    await event.reply(required_string.format(p))


@register(pattern="^/kickme$")
async def kickme(bon):
    if not bon.is_group:
        return
    try:
        await tbot.kick_participant(bon.chat_id, bon.sender_id)
        await bon.reply("Ok Kicked !")
    except Exception as e:
        await bon.reply("Failed to kick !")
        return



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


@register(pattern="^/unlock ?(.*)")
async def rem_locks(event):
    if not event.is_group:
        return
    if event.is_group:
        if not await can_change_info(message=event):
            print("not enough perms")
            return
    input_str = event.pattern_match.group(1).lower()
    # print(input_str)
    peer_id = event.chat_id
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
        msg = False
        what = "messages"
    elif input_str == "media":
        media = False
        what = "media"
    elif input_str == "sticker":
        sticker = False
        what = "stickers"
    elif input_str == "gif":
        gif = False
        what = "GIFs"
    elif input_str == "game":
        gamee = False
        what = "games"
    elif input_str == "inline":
        ainline = False
        what = "inline bots"
    elif input_str == "poll":
        gpoll = False
        what = "polls"
    elif input_str == "invite":
        adduser = False
        what = "invites"
    elif input_str == "pin":
        cpin = False
        what = "pins"
    elif input_str == "url":
        emlink = False
        what = "url links"
    elif input_str == "info":
        changeinfo = False
        what = "chat info"
    elif input_str == "all":
        msg = False
        media = False
        sticker = False
        gif = False
        gamee = False
        emlink = False
        ainline = False
        gpoll = False
        adduser = False
        cpin = False
        changeinfo = False
        what = "everything"
    else:
        if not input_str:
            await event.reply("I can't unlock nothing !!")
            return
        await event.reply(f"Invalid unlock type: {input_str}")
        return

    unlock_rights = ChatBannedRights(
        until_date=None,
        send_messages=msg,
        send_media=media,
        send_stickers=sticker,
        send_gifs=gif,
        send_games=gamee,
        embed_links=emlink,
        send_inline=ainline,
        send_polls=gpoll,
        invite_users=adduser,
        pin_messages=cpin,
        change_info=changeinfo,
    )

    # print(input_str)
    # print (unlock_rights)
    try:
        await tbot(
            EditChatDefaultBannedRightsRequest(
                event.chat_id, banned_rights=unlock_rights
            )
        )
        await event.reply(f"Unlocked Successfully !")
    except Exception:
        await event.reply("Failed to unlock.")
        return


@register(pattern="^/chatlocktypes$")
async def ltypes(event):
    if not event.is_group:
        return
    if event.is_group:
        if not await can_ban_users(message=event):
            return
    await event.reply(
        "**These are the valid lock types:**\n\nmsg\nmedia\nurl\nsticker\ngif\ngame\ninline\npoll\ninvite\npin\ninfo\nall"
    )


@register(pattern="^/chatlocks$")
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



@register(pattern="^/setgrouptitle (.*)")
async def set_group_title(gpic):
    input_str = gpic.pattern_match.group(1)

    if gpic.is_group:
        if not await can_change_info(message=gpic):
            return
    else:
        return

    try:
        await tbot(
            functions.messages.EditChatTitleRequest(
                chat_id=gpic.chat_id, title=input_str
            )
        )
    except BaseException:
        await tbot(
            functions.channels.EditTitleRequest(channel=gpic.chat_id, title=input_str)
        )

    if gpic.chat.title == input_str:
        await gpic.reply("Successfully set new group title.")
    else:
        await gpic.reply("Failed to set group title.")


@register(pattern=r"^/setdescription ([\s\S]*)")
async def set_group_des(gpic):
    input_str = gpic.pattern_match.group(1)
    # print(input_str)
    if gpic.is_group:
        if not await can_change_info(message=gpic):
            return
    else:
        return

    try:
        await tbot(
            functions.messages.EditChatAboutRequest(peer=gpic.chat_id, about=input_str)
        )
        await gpic.reply("Successfully set new group description.")
    except BaseException:
        await gpic.reply("Failed to set group description.")


@register(pattern="^/setsticker$")
async def set_group_sticker(gpic):
    if gpic.is_group:
        if not await can_change_info(message=gpic):
            return
    else:
        return

    rep_msg = await gpic.get_reply_message()
    if not rep_msg.document:
        await gpic.reply("Reply to any sticker plox.")
        return
    stickerset_attr_s = rep_msg.document.attributes
    stickerset_attr = find_instance(stickerset_attr_s, DocumentAttributeSticker)
    if not stickerset_attr.stickerset:
        await gpic.reply("Sticker does not belong to a pack.")
        return
    try:
        id = stickerset_attr.stickerset.id
        access_hash = stickerset_attr.stickerset.access_hash
        print(id)
        print(access_hash)
        await tbot(
            functions.channels.SetStickersRequest(
                channel=gpic.chat_id,
                stickerset=types.InputStickerSetID(id=id, access_hash=access_hash),
            )
        )
        await gpic.reply("Group sticker pack successfully set !")
    except Exception as e:
        print(e)
        await gpic.reply("Failed to set group sticker pack.")


async def extract_time(message, time_val):
    if any(time_val.endswith(unit) for unit in ("m", "h", "d")):
        unit = time_val[-1]
        time_num = time_val[:-1]  # type: str
        if not time_num.isdigit():
            await message.reply("Invalid time amount specified.")
            return None

        if unit == "m":
            bantime = int(time.time() + int(time_num) * 60)
        elif unit == "h":
            bantime = int(time.time() + int(time_num) * 60 * 60)
        elif unit == "d":
            bantime = int(time.time() + int(time_num) * 24 * 60 * 60)
        else:
            return
        return bantime
    else:
        return None


__help__ = """
 - /adminlist : list of admins in the chat
 - /pin <loud(optional)> | /unpin: pins/unpins the message in the chat
 - /promote: promotes a user
 - /demote: demotes a user
 - /ban: bans a user
 - /unban: unbans a user
 - /mute: mute a user
 - /unmute: unmutes a user
 - /tban <entity> | <time interval>: temporarily bans a user for the time interval.
 - /tmute <entity> | <time interval>: temporarily mutes a user for the time interval.
 - /kick: kicks a user
 - /kickme: kicks yourself (non-admins)
 - /banme: bans yourself (non-admins)
 - /settitle <entity> <title>: sets a custom title for an admin. If no <title> provided defaults to "Admin"
 - /setdescription <text>: set group description
 - /setgrouptitle <text>: set group title
 - /setgpic: reply to an image to set as group photo
 - /setsticker: reply to a sticker pack to set as group stickers
 - /delgpic: deletes the current group photo
 - /purge: deletes all messages from the message you replied to
 - /del: deletes the message replied to
 - /lock <item(s)>: lock the usage of "item" for non-admins
 - /unlock <item(s)>: unlock "item". Everyone can use them again
 - /chatlocks: gives the lock status of the chat
 - /chatlocktypes: gets a list of all things that can be locked
 - /unbanall: Unbans all in the chat
 - /unmuteall: Unmutes all in the chat
 - /users: list all the users in the chat
 - /zombies: counts the number of deleted account in your group
 - /kickthefools: kicks all members inactive from 1 week
"""




__mod_name__ = "Locks"
