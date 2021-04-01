#    Copyright (C) 2020-2021 by @InukaAsith
#    This programme is a part of Liza TG bot project
#
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


import logging
import time

from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import (
    ChatAdminRequired,
    PeerIdInvalid,
    UsernameNotOccupied,
    UserNotParticipant,
)
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup

# from DaisyX import OWNER_ID as SUDO_USERS
from DaisyX.services.pyrogram import pbot
from DaisyX.services.sql import forceSubscribe_sql as sql

logging.basicConfig(level=logging.INFO)

static_data_filter = filters.create(
    lambda _, __, query: query.data == "onUnMuteRequest"
)


@pbot.on_callback_query(static_data_filter)
def _onUnMuteRequest(client, cb):
    user_id = cb.from_user.id
    chat_id = cb.message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        channel = chat_db.channel
        chat_member = client.get_chat_member(chat_id, user_id)
        if chat_member.restricted_by:
            if chat_member.restricted_by.id == (client.get_me()).id:
                try:
                    client.get_chat_member(channel, user_id)
                    client.unban_chat_member(chat_id, user_id)
                    cb.message.delete()
                    # if cb.message.reply_to_message.from_user.id == user_id:
                    # cb.message.delete()
                except UserNotParticipant:
                    client.answer_callback_query(
                        cb.id,
                        text=f"❗ Join our @{channel} channel and press 'UnMute Me' button.",
                        show_alert=True,
                    )
            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ You have been muted by admins due to some other reason.",
                    show_alert=True,
                )
        else:
            if (
                not client.get_chat_member(chat_id, (client.get_me()).id).status
                == "administrator"
            ):
                client.send_message(
                    chat_id,
                    f"❗ **{cb.from_user.mention} is trying to UnMute himself but i can't unmute him because i am not an admin in this chat add me as admin again.**\n__#Leaving this chat...__",
                )

            else:
                client.answer_callback_query(
                    cb.id,
                    text="❗ Warning! Don't press the button when you cn talk.",
                    show_alert=True,
                )


@pbot.on_message(filters.text & ~filters.private & ~filters.edited, group=1)
def _check_member(client, message):
    chat_id = message.chat.id
    chat_db = sql.fs_settings(chat_id)
    if chat_db:
        user_id = message.from_user.id
        if (
            not client.get_chat_member(chat_id, user_id).status
            in ("administrator", "creator")
            and not user_id == 1141839926
        ):
            channel = chat_db.channel
            try:
                client.get_chat_member(channel, user_id)
            except UserNotParticipant:
                try:
                    sent_message = message.reply_text(
                        "Welcome {} 🙏 \n **You havent joined our @{} Channel yet** 😭 \n \nPlease Join [Our Channel](https://t.me/{}) and hit the **UNMUTE ME** Button. \n \n ".format(
                            message.from_user.mention, channel, channel
                        ),
                        disable_web_page_preview=True,
                        reply_markup=InlineKeyboardMarkup(
                            [
                                [
                                    InlineKeyboardButton(
                                        "Join Channel",
                                        url="https://t.me/{}".format(channel),
                                    )
                                ],
                                [
                                    InlineKeyboardButton(
                                        "UnMute Me", callback_data="onUnMuteRequest"
                                    )
                                ],
                            ]
                        ),
                    )
                    client.restrict_chat_member(
                        chat_id, user_id, ChatPermissions(can_send_messages=False)
                    )
                except ChatAdminRequired:
                    sent_message.edit(
                        "❗ **Daisy is not admin here..**\n__Give me ban permissions and retry.. \n#Ending FSub...__"
                    )

            except ChatAdminRequired:
                client.send_message(
                    chat_id,
                    text=f"❗ **I not an admin of @{channel} channel.**\n__Give me admin of that channel and retry.\n#Ending FSub...__",
                )


@pbot.on_message(filters.command(["forcesubscribe", "forcesub"]) & ~filters.private)
def config(client, message):
    user = client.get_chat_member(message.chat.id, message.from_user.id)
    if user.status is "creator" or user.user.id == 1141839926:
        chat_id = message.chat.id
        if len(message.command) > 1:
            input_str = message.command[1]
            input_str = input_str.replace("@", "")
            if input_str.lower() in ("off", "no", "disable"):
                sql.disapprove(chat_id)
                message.reply_text("❌ **Force Subscribe is Disabled Successfully.**")
            elif input_str.lower() in ("clear"):
                sent_message = message.reply_text(
                    "**Unmuting all members who are muted by me...**"
                )
                try:
                    for chat_member in client.get_chat_members(
                        message.chat.id, filter="restricted"
                    ):
                        if chat_member.restricted_by.id == (client.get_me()).id:
                            client.unban_chat_member(chat_id, chat_member.user.id)
                            time.sleep(1)
                    sent_message.edit("✅ **UnMuted all members who are muted by me.**")
                except ChatAdminRequired:
                    sent_message.edit(
                        "❗ **I am not an admin in this chat.**\n__I can't unmute members because i am not an admin in this chat make me admin with ban user permission.__"
                    )
            else:
                try:
                    client.get_chat_member(input_str, "me")
                    sql.add_channel(chat_id, input_str)
                    message.reply_text(
                        f"✅ **Force Subscribe is Enabled**\n__Force Subscribe is enabled, all the group members have to subscribe this [channel](https://t.me/{input_str}) in order to send messages in this group.__",
                        disable_web_page_preview=True,
                    )
                except UserNotParticipant:
                    message.reply_text(
                        f"❗ **Not an Admin in the Channel**\n__I am not an admin in the [channel](https://t.me/{input_str}). Add me as a admin in order to enable ForceSubscribe.__",
                        disable_web_page_preview=True,
                    )
                except (UsernameNotOccupied, PeerIdInvalid):
                    message.reply_text(f"❗ **Invalid Channel Username.**")
                except Exception as err:
                    message.reply_text(f"❗ **ERROR:** ```{err}```")
        else:
            if sql.fs_settings(chat_id):
                message.reply_text(
                    f"✅ **Force Subscribe is enabled in this chat.**\n__For this [Channel](https://t.me/{sql.fs_settings(chat_id).channel})__",
                    disable_web_page_preview=True,
                )
            else:
                message.reply_text("❌ **Force Subscribe is disabled in this chat.**")
    else:
        message.reply_text(
            "❗ **Group Creator Required**\n__You have to be the group creator to do that.__"
        )


__help__ = """
*ForceSubscribe:*
✪ Daisy can mute members who are not subscribed your channel until they subscribe
✪ When enabled I will mute unsubscribed members and show them a unmute button. When they pressed the button I will unmute them
*Setup*
1) First of all add me in the group as admin with ban users permission and in the channel as admin.
Note: Only creator of the group can setup me and i will not allow force subscribe again if not done so.
 
*Commmands*
 - /forcesubscribe - To get the current settings.
 - /forcesubscribe no/off/disable - To turn of ForceSubscribe.
 - /forcesubscribe {channel username} - To turn on and setup the channel.
 - /forcesubscribe clear - To unmute all members who muted by me.
Note: /forcesub is an alias of /forcesubscribe
 
"""
__mod_name__ = "Force Subscribe "
