"""
MIT License
Copyright (c) 2021 TheHamkerCat
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import os

from pyrogram import filters

from DaisyX.function.pluginhelpers import member_permissions
from DaisyX.services.pyrogram import pbot as app


@app.on_message(filters.command("setgrouptitle") & ~filters.private)
async def set_chat_title(_, message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        permissions = await member_permissions(chat_id, user_id)
        if "can_change_info" not in permissions:
            await message.reply_text("You Don't Have Enough Permissions.")
            return
        if len(message.command) < 2:
            await message.reply_text("**Usage:**\n/set_chat_title NEW NAME")
            return
        old_title = message.chat.title
        new_title = message.text.split(None, 1)[1]
        await message.chat.set_title(new_title)
        await message.reply_text(
            f"Successfully Changed Group Title From {old_title} To {new_title}"
        )
    except Exception as e:
        print(e)
        await message.reply_text(e)


@app.on_message(filters.command("settitle") & ~filters.private)
async def set_user_title(_, message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id
        from_user = message.reply_to_message.from_user
        permissions = await member_permissions(chat_id, user_id)
        if "can_change_info" not in permissions:
            await message.reply_text("You Don't Have Enough Permissions.")
            return
        if len(message.command) < 2:
            await message.reply_text(
                "**Usage:**\n/set_user_title NEW ADMINISTRATOR TITLE"
            )
            return
        title = message.text.split(None, 1)[1]
        await app.set_administrator_title(chat_id, from_user.id, title)
        await message.reply_text(
            f"Successfully Changed {from_user.mention}'s Admin Title To {title}"
        )
    except Exception as e:
        print(e)
        await message.reply_text(e)


@app.on_message(filters.command("setgrouppic") & ~filters.private)
async def set_chat_photo(_, message):
    try:
        chat_id = message.chat.id
        user_id = message.from_user.id

        permissions = await member_permissions(chat_id, user_id)
        if "can_change_info" not in permissions:
            await message.reply_text("You Don't Have Enough Permissions.")
            return
        if not message.reply_to_message:
            await message.reply_text("Reply to a photo to set it as chat_photo")
            return
        if not message.reply_to_message.photo and not message.reply_to_message.document:
            await message.reply_text("Reply to a photo to set it as chat_photo")
            return
        photo = await message.reply_to_message.download()
        await message.chat.set_photo(photo)
        await message.reply_text("Successfully Changed Group Photo")
        os.remove(photo)
    except Exception as e:
        print(e)
        await message.reply_text(e)


__mod_name__ = "Admin"

__help__ = """
Make it easy to admins for manage users and groups with the admin module!

<b>Available commands:</b>

<b> Admin List </b>
- /adminlist: Shows all admins of the chat.*
- /admincache: Update the admin cache, to take into account new admins/admin permissions.*

<b> Mutes </b>
- /mute: mute a user
- /unmute: unmutes a user
- /tmute [entity] : temporarily mutes a user for the time interval.
- /unmuteall: Unmute all muted members

<b> Bans & Kicks </b>
- /ban: bans a user
- /tban [entity] : temporarily bans a user for the time interval.
- /unban: unbans a user
- /unbanall: Unban all banned members
- /banme: Bans you
- /kick: kicks a user
- /kickme: Kicks you

<b> Promotes & Demotes</b>
- /promote (user) (?admin's title): Promotes the user to admin.*
- /demote (user): Demotes the user from admin.*
- /lowpromote: Promote a member with low rights*
- /midpromote: Promote a member with mid rights*
- /highpromote: Promote a member with max rights*
- /lowdemote: Demote an admin to low permissions*
- /middemote: Demote an admin to mid permissions*

<b> Cleaner/Purges </b>
- /purge: deletes all messages from the message you replied to
- /del: deletes the message replied to
- /zombies: counts the number of deleted account in your group
- /kickthefools: Kick inactive members from group (one week)

<b> User Info </b>
- /info: Get user's info
- /users: Get users list of group
- /spwinfo : Check user's spam info from intellivoid's Spamprotection service
- /whois : Gives user's info like pyrogram

<b> Other </b>
- /invitelink: Get chat's invitr link
- /settitle [entity] [title]: sets a custom title for an admin. If no [title] provided defaults to "Admin"
- /setgrouptitle [text] set group title
- /setgrouppic: reply to an image to set as group photo
- /setdescription: Set group description
- /setsticker: Set group sticker

*Note:
Sometimes, you promote or demote an admin manually, and Daisy doesn't realise it immediately. This is because to avoid spamming telegram servers, admin status is cached locally.
This means that you sometimes have to wait a few minutes for admin rights to update. If you want to update them immediately, you can use the /admincache command; that'll force Daisy to check who the admins are again.
"""
