# Copyright (C) 2018 - 2020 MrYacha. All rights reserved. Source code available under the AGPL.
# Copyright (C) 2021 TeamDaisyX
# Copyright (C) 2020 Inuka Asith

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

from DaisyX.decorator import register
from DaisyX.services.mongo import db

from .utils.connections import chat_connection
from .utils.disable import disableable_dec
from .utils.language import get_strings_dec
from .utils.user_details import get_admins_rights, get_user_link, is_user_admin


@register(regexp="^@admin$")
@chat_connection(only_groups=True)
@get_strings_dec("reports")
async def report1_cmd(message, chat, strings):
    # Checking whether report is disabled in chat!
    check = await db.disabled.find_one({"chat_id": chat["chat_id"]})
    if check:
        if "report" in check["cmds"]:
            return
    await report(message, chat, strings)


@register(cmds="report")
@chat_connection(only_groups=True)
@disableable_dec("report")
@get_strings_dec("reports")
async def report2_cmd(message, chat, strings):
    await report(message, chat, strings)


async def report(message, chat, strings):
    user = message.from_user.id

    if (await is_user_admin(chat["chat_id"], user)) is True:
        return await message.reply(strings["user_user_admin"])

    if "reply_to_message" not in message:
        return await message.reply(strings["no_user_to_report"])

    offender_id = message.reply_to_message.from_user.id
    if (await is_user_admin(chat["chat_id"], offender_id)) is True:
        return await message.reply(strings["report_admin"])

    admins = await get_admins_rights(chat["chat_id"])

    offender = await get_user_link(offender_id)
    text = strings["reported_user"].format(user=offender)

    try:
        if message.text.split(None, 2)[1]:
            reason = " ".join(message.text.split(None, 2)[1:])
            text += strings["reported_reason"].format(reason=reason)
    except IndexError:
        pass

    for admin in admins:
        text += await get_user_link(admin, custom_name="​")

    await message.reply(text)


__mod_name__ = "Reports"

__help__ = """
We're all busy people who don't have time to monitor our groups 24/7. But how do you react if someone in your group is spamming?

Presenting reports; if someone in your group thinks someone needs reporting, they now have an easy way to call all admins.

<b>Available commands:</b>
- /report (?text): Reports
- @admins: Same as above, but not a clickable

<b>TIP:</b> You always can disable reporting by disabling module
"""
