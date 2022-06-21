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

from dataclasses import dataclass

from aiogram.dispatcher.filters import Filter
from aiogram.types.callback_query import CallbackQuery
from aiogram.utils.exceptions import BadRequest

from DaisyX import BOT_ID, dp
from DaisyX.modules.utils.language import get_strings
from DaisyX.modules.utils.user_details import check_admin_rights


@dataclass
class UserRestricting(Filter):
    admin: bool = False
    can_post_messages: bool = False
    can_edit_messages: bool = False
    can_delete_messages: bool = False
    can_restrict_members: bool = False
    can_promote_members: bool = False
    can_change_info: bool = False
    can_invite_users: bool = False
    can_pin_messages: bool = False

    ARGUMENTS = {
        "user_admin": "admin",
        "user_can_post_messages": "can_post_messages",
        "user_can_edit_messages": "can_edit_messages",
        "user_can_delete_messages": "can_delete_messages",
        "user_can_restrict_members": "can_restrict_members",
        "user_can_promote_members": "can_promote_members",
        "user_can_change_info": "can_change_info",
        "user_can_invite_users": "can_invite_users",
        "user_can_pin_messages": "can_pin_messages",
    }
    PAYLOAD_ARGUMENT_NAME = "user_member"

    def __post_init__(self):
        self.required_permissions = {
            arg: True for arg in self.ARGUMENTS.values() if getattr(self, arg)
        }

    @classmethod
    def validate(cls, full_config):
        return {
            argument: full_config.pop(alias)
            for alias, argument in cls.ARGUMENTS.items()
            if alias in full_config
        }

    async def check(self, event):
        user_id = await self.get_target_id(event)
        message = event.message if hasattr(event, "message") else event
        # If pm skip checks
        if message.chat.type == "private":
            return True

        check = await check_admin_rights(
            message, message.chat.id, user_id, self.required_permissions.keys()
        )
        if check is not True:
            # check = missing permission in this scope
            await self.no_rights_msg(event, check)
            return False

        return True

    async def get_target_id(self, message):
        return message.from_user.id

    async def no_rights_msg(self, message, required_permissions):
        strings = await get_strings(
            message.message.chat.id if hasattr(message, "message") else message.chat.id,
            "global",
        )
        task = message.answer if hasattr(message, "message") else message.reply
        if not isinstance(
            required_permissions, bool
        ):  # Check if check_admin_rights func returned missing perm
            required_permissions = " ".join(
                required_permissions.strip("can_").split("_")
            )
            try:
                await task(
                    strings["user_no_right"].format(permission=required_permissions)
                )
            except BadRequest as error:
                if error.args == "Reply message not found":
                    return await message.answer(strings["user_no_right"])
        else:
            try:
                await task(strings["user_no_right:not_admin"])
            except BadRequest as error:
                if error.args == "Reply message not found":
                    return await message.answer(strings["user_no_right:not_admin"])


class BotHasPermissions(UserRestricting):
    ARGUMENTS = {
        "bot_admin": "admin",
        "bot_can_post_messages": "can_post_messages",
        "bot_can_edit_messages": "can_edit_messages",
        "bot_can_delete_messages": "can_delete_messages",
        "bot_can_restrict_members": "can_restrict_members",
        "bot_can_promote_members": "can_promote_members",
        "bot_can_change_info": "can_change_info",
        "bot_can_invite_users": "can_invite_users",
        "bot_can_pin_messages": "can_pin_messages",
    }
    PAYLOAD_ARGUMENT_NAME = "bot_member"

    async def get_target_id(self, message):
        return BOT_ID

    async def no_rights_msg(self, message, required_permissions):
        message = message.message if isinstance(message, CallbackQuery) else message
        strings = await get_strings(message.chat.id, "global")
        if not isinstance(required_permissions, bool):
            required_permissions = " ".join(
                required_permissions.strip("can_").split("_")
            )
            try:
                await message.reply(
                    strings["bot_no_right"].format(permission=required_permissions)
                )
            except BadRequest as error:
                if error.args == "Reply message not found":
                    return await message.answer(strings["bot_no_right"])
        else:
            try:
                await message.reply(strings["bot_no_right:not_admin"])
            except BadRequest as error:
                if error.args == "Reply message not found":
                    return await message.answer(strings["bot_no_right:not_admin"])


dp.filters_factory.bind(UserRestricting)
dp.filters_factory.bind(BotHasPermissions)
