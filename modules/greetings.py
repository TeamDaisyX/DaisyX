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

import html
import io
import random
import re
from contextlib import suppress
from datetime import datetime
from typing import Optional, Union

from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery, ContentType, Message
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.input_media import InputMediaPhoto
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import (
    BadRequest,
    ChatAdminRequired,
    MessageCantBeDeleted,
    MessageToDeleteNotFound,
)
from apscheduler.jobstores.base import JobLookupError
from babel.dates import format_timedelta
from captcha.image import ImageCaptcha
from telethon.tl.custom import Button

from DaisyX import BOT_ID, BOT_USERNAME, LOGS_CHANNEL_ID, bot, dp
from DaisyX.config import get_str_key
from DaisyX.decorator import register
from DaisyX.services.apscheduller import scheduler
from DaisyX.services.mongo import db
from DaisyX.services.redis import redis
from DaisyX.services.telethon import tbot
from DaisyX.stuff.fonts import ALL_FONTS

from ..utils.cached import cached
from .utils.connections import chat_connection
from .utils.language import get_strings_dec
from .utils.message import convert_time, need_args_dec
from .utils.notes import get_parsed_note_list, send_note, t_unparse_note_item
from .utils.restrictions import kick_user, mute_user, restrict_user, unmute_user
from .utils.user_details import check_admin_rights, get_user_link, is_user_admin


class WelcomeSecurityState(StatesGroup):
    button = State()
    captcha = State()
    math = State()


@register(cmds="welcome")
@chat_connection(only_groups=True)
@get_strings_dec("greetings")
async def welcome(message, chat, strings):
    chat_id = chat["chat_id"]
    send_id = message.chat.id

    if len(args := message.get_args().split()) > 0:
        no_format = True if "no_format" == args[0] or "raw" == args[0] else False
    else:
        no_format = None

    if not (db_item := await get_greetings_data(chat_id)):
        db_item = {}
    if "note" not in db_item:
        db_item["note"] = {"text": strings["default_welcome"]}

    if no_format:
        await message.reply(strings["raw_wlcm_note"])
        text, kwargs = await t_unparse_note_item(
            message, db_item["note"], chat_id, noformat=True
        )
        await send_note(send_id, text, **kwargs)
        return

    text = strings["welcome_info"]

    text = text.format(
        chat_name=chat["chat_title"],
        welcomes_status=strings["disabled"]
        if "welcome_disabled" in db_item and db_item["welcome_disabled"] is True
        else strings["enabled"],
        wlcm_security=strings["disabled"]
        if "welcome_security" not in db_item
        or db_item["welcome_security"]["enabled"] is False
        else strings["wlcm_security_enabled"].format(
            level=db_item["welcome_security"]["level"]
        ),
        wlcm_mutes=strings["disabled"]
        if "welcome_mute" not in db_item or db_item["welcome_mute"]["enabled"] is False
        else strings["wlcm_mutes_enabled"].format(time=db_item["welcome_mute"]["time"]),
        clean_welcomes=strings["enabled"]
        if "clean_welcome" in db_item and db_item["clean_welcome"]["enabled"] is True
        else strings["disabled"],
        clean_service=strings["enabled"]
        if "clean_service" in db_item and db_item["clean_service"]["enabled"] is True
        else strings["disabled"],
    )
    if "welcome_disabled" not in db_item:
        text += strings["wlcm_note"]
        await message.reply(text)
        text, kwargs = await t_unparse_note_item(message, db_item["note"], chat_id)
        await send_note(send_id, text, **kwargs)
    else:
        await message.reply(text)

    if "welcome_security" in db_item:
        if "security_note" not in db_item:
            db_item["security_note"] = {"text": strings["default_security_note"]}
        await message.reply(strings["security_note"])
        text, kwargs = await t_unparse_note_item(
            message, db_item["security_note"], chat_id
        )
        await send_note(send_id, text, **kwargs)


@register(
    cmds=["setwelcome", "savewelcome"], user_admin=True, user_can_change_info=True
)
@chat_connection(admin=True, only_groups=True)
@get_strings_dec("greetings")
async def set_welcome(message, chat, strings):
    chat_id = chat["chat_id"]

    if len(args := message.get_args().lower().split()) < 1:
        db_item = await get_greetings_data(chat_id)

        if (
            db_item
            and "welcome_disabled" in db_item
            and db_item["welcome_disabled"] is True
        ):
            status = strings["disabled"]
        else:
            status = strings["enabled"]

        await message.reply(
            strings["turnwelcome_status"].format(
                status=status, chat_name=chat["chat_title"]
            )
        )
        return

    no = ["no", "off", "0", "false", "disable"]

    if args[0] in no:
        await db.greetings.update_one(
            {"chat_id": chat_id},
            {"$set": {"chat_id": chat_id, "welcome_disabled": True}},
            upsert=True,
        )
        await get_greetings_data.reset_cache(chat_id)
        await message.reply(strings["turnwelcome_disabled"] % chat["chat_title"])
        return
    else:
        note = await get_parsed_note_list(message, split_args=-1)

        if (
            await db.greetings.update_one(
                {"chat_id": chat_id},
                {
                    "$set": {"chat_id": chat_id, "note": note},
                    "$unset": {"welcome_disabled": 1},
                },
                upsert=True,
            )
        ).modified_count > 0:
            text = strings["updated"]
        else:
            text = strings["saved"]

        await get_greetings_data.reset_cache(chat_id)
        await message.reply(text % chat["chat_title"])


@register(cmds="resetwelcome", user_admin=True, user_can_change_info=True)
@chat_connection(admin=True, only_groups=True)
@get_strings_dec("greetings")
async def reset_welcome(message, chat, strings):
    chat_id = chat["chat_id"]

    if (await db.greetings.delete_one({"chat_id": chat_id})).deleted_count < 1:
        await get_greetings_data.reset_cache(chat_id)
        await message.reply(strings["not_found"])
        return

    await get_greetings_data.reset_cache(chat_id)
    await message.reply(strings["deleted"].format(chat=chat["chat_title"]))


@register(cmds="cleanwelcome", user_admin=True)
@chat_connection(admin=True, only_groups=True)
@get_strings_dec("greetings")
async def clean_welcome(message, chat, strings):
    chat_id = chat["chat_id"]

    if len(args := message.get_args().lower().split()) < 1:
        db_item = await get_greetings_data(chat_id)

        if (
            db_item
            and "clean_welcome" in db_item
            and db_item["clean_welcome"]["enabled"] is True
        ):
            status = strings["enabled"]
        else:
            status = strings["disabled"]

        await message.reply(
            strings["cleanwelcome_status"].format(
                status=status, chat_name=chat["chat_title"]
            )
        )
        return

    yes = ["yes", "on", "1", "true", "enable"]
    no = ["no", "off", "0", "false", "disable"]

    if args[0] in yes:
        await db.greetings.update_one(
            {"chat_id": chat_id},
            {"$set": {"chat_id": chat_id, "clean_welcome": {"enabled": True}}},
            upsert=True,
        )
        await get_greetings_data.reset_cache(chat_id)
        await message.reply(strings["cleanwelcome_enabled"] % chat["chat_title"])
    elif args[0] in no:
        await db.greetings.update_one(
            {"chat_id": chat_id}, {"$unset": {"clean_welcome": 1}}, upsert=True
        )
        await get_greetings_data.reset_cache(chat_id)
        await message.reply(strings["cleanwelcome_disabled"] % chat["chat_title"])
    else:
        await message.reply(strings["bool_invalid_arg"])


@register(cmds="cleanservice", user_admin=True, user_can_change_info=True)
@chat_connection(admin=True, only_groups=True)
@get_strings_dec("greetings")
async def clean_service(message, chat, strings):
    chat_id = chat["chat_id"]

    if len(args := message.get_args().lower().split()) < 1:
        db_item = await get_greetings_data(chat_id)

        if (
            db_item
            and "clean_service" in db_item
            and db_item["clean_service"]["enabled"] is True
        ):
            status = strings["enabled"]
        else:
            status = strings["disabled"]

        await message.reply(
            strings["cleanservice_status"].format(
                status=status, chat_name=chat["chat_title"]
            )
        )
        return

    yes = ["yes", "on", "1", "true", "enable"]
    no = ["no", "off", "0", "false", "disable"]

    if args[0] in yes:
        await db.greetings.update_one(
            {"chat_id": chat_id},
            {"$set": {"chat_id": chat_id, "clean_service": {"enabled": True}}},
            upsert=True,
        )
        await get_greetings_data.reset_cache(chat_id)
        await message.reply(strings["cleanservice_enabled"] % chat["chat_title"])
    elif args[0] in no:
        await db.greetings.update_one(
            {"chat_id": chat_id}, {"$unset": {"clean_service": 1}}, upsert=True
        )
        await get_greetings_data.reset_cache(chat_id)
        await message.reply(strings["cleanservice_disabled"] % chat["chat_title"])
    else:
        await message.reply(strings["bool_invalid_arg"])


@register(cmds="welcomemute", user_admin=True, user_can_change_info=True)
@chat_connection(admin=True, only_groups=True)
@get_strings_dec("greetings")
async def welcome_mute(message, chat, strings):
    chat_id = chat["chat_id"]

    if len(args := message.get_args().lower().split()) < 1:
        db_item = await get_greetings_data(chat_id)

        if (
            db_item
            and "welcome_mute" in db_item
            and db_item["welcome_mute"]["enabled"] is True
        ):
            status = strings["enabled"]
        else:
            status = strings["disabled"]

        await message.reply(
            strings["welcomemute_status"].format(
                status=status, chat_name=chat["chat_title"]
            )
        )
        return

    no = ["no", "off", "0", "false", "disable"]

    if args[0].endswith(("m", "h", "d")):
        await db.greetings.update_one(
            {"chat_id": chat_id},
            {
                "$set": {
                    "chat_id": chat_id,
                    "welcome_mute": {"enabled": True, "time": args[0]},
                }
            },
            upsert=True,
        )
        await get_greetings_data.reset_cache(chat_id)
        text = strings["welcomemute_enabled"] % chat["chat_title"]
        try:
            await message.reply(text)
        except BadRequest:
            await message.answer(text)
    elif args[0] in no:
        text = strings["welcomemute_disabled"] % chat["chat_title"]
        await db.greetings.update_one(
            {"chat_id": chat_id}, {"$unset": {"welcome_mute": 1}}, upsert=True
        )
        await get_greetings_data.reset_cache(chat_id)
        try:
            await message.reply(text)
        except BadRequest:
            await message.answer(text)
    else:
        text = strings["welcomemute_invalid_arg"]
        try:
            await message.reply(text)
        except BadRequest:
            await message.answer(text)


# Welcome Security

wlcm_sec_config_proc = CallbackData("wlcm_sec_proc", "chat_id", "user_id", "level")
wlcm_sec_config_cancel = CallbackData("wlcm_sec_cancel", "user_id", "level")


class WelcomeSecurityConf(StatesGroup):
    send_time = State()


@register(cmds="welcomesecurity", user_admin=True, user_can_change_info=True)
@chat_connection(admin=True, only_groups=True)
@get_strings_dec("greetings")
async def welcome_security(message, chat, strings):
    chat_id = chat["chat_id"]

    if len(args := message.get_args().lower().split()) < 1:
        db_item = await get_greetings_data(chat_id)

        if (
            db_item
            and "welcome_security" in db_item
            and db_item["welcome_security"]["enabled"] is True
        ):
            status = strings["welcomesecurity_enabled_word"].format(
                level=db_item["welcome_security"]["level"]
            )
        else:
            status = strings["disabled"]

        await message.reply(
            strings["welcomesecurity_status"].format(
                status=status, chat_name=chat["chat_title"]
            )
        )
        return

    no = ["no", "off", "0", "false", "disable"]

    if args[0].lower() in ["button", "math", "captcha"]:
        level = args[0].lower()
    elif args[0] in no:
        await db.greetings.update_one(
            {"chat_id": chat_id}, {"$unset": {"welcome_security": 1}}, upsert=True
        )
        await get_greetings_data.reset_cache(chat_id)
        await message.reply(strings["welcomesecurity_disabled"] % chat["chat_title"])
        return
    else:
        await message.reply(strings["welcomesecurity_invalid_arg"])
        return

    await db.greetings.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "chat_id": chat_id,
                "welcome_security": {"enabled": True, "level": level},
            }
        },
        upsert=True,
    )
    await get_greetings_data.reset_cache(chat_id)
    buttons = InlineKeyboardMarkup()
    buttons.add(
        InlineKeyboardButton(
            strings["no_btn"],
            callback_data=wlcm_sec_config_cancel.new(
                user_id=message.from_user.id, level=level
            ),
        ),
        InlineKeyboardButton(
            strings["yes_btn"],
            callback_data=wlcm_sec_config_proc.new(
                chat_id=chat_id, user_id=message.from_user.id, level=level
            ),
        ),
    )
    await message.reply(
        strings["ask_for_time_customization"].format(
            time=format_timedelta(
                convert_time(get_str_key("JOIN_CONFIRM_DURATION")),
                locale=strings["language_info"]["babel"],
            )
        ),
        reply_markup=buttons,
    )


@register(wlcm_sec_config_cancel.filter(), f="cb", allow_kwargs=True)
@chat_connection(admin=True)
@get_strings_dec("greetings")
async def welcome_security_config_cancel(
    event: CallbackQuery, chat: dict, strings: dict, callback_data: dict, **_
):
    if int(callback_data["user_id"]) == event.from_user.id and is_user_admin(
        chat["chat_id"], event.from_user.id
    ):
        await event.message.edit_text(
            text=strings["welcomesecurity_enabled"].format(
                chat_name=chat["chat_title"], level=callback_data["level"]
            )
        )


@register(wlcm_sec_config_proc.filter(), f="cb", allow_kwargs=True)
@chat_connection(admin=True)
@get_strings_dec("greetings")
async def welcome_security_config_proc(
    event: CallbackQuery, chat: dict, strings: dict, callback_data: dict, **_
):
    if int(callback_data["user_id"]) != event.from_user.id and is_user_admin(
        chat["chat_id"], event.from_user.id
    ):
        return

    await WelcomeSecurityConf.send_time.set()
    async with dp.get_current().current_state().proxy() as data:
        data["level"] = callback_data["level"]
    await event.message.edit_text(strings["send_time"])


@register(
    state=WelcomeSecurityConf.send_time,
    content_types=ContentType.TEXT,
    allow_kwargs=True,
)
@chat_connection(admin=True)
@get_strings_dec("greetings")
async def wlcm_sec_time_state(message: Message, chat: dict, strings: dict, state, **_):
    async with state.proxy() as data:
        level = data["level"]
    try:
        con_time = convert_time(message.text)
    except (ValueError, TypeError):
        await message.reply(strings["invalid_time"])
    else:
        await db.greetings.update_one(
            {"chat_id": chat["chat_id"]},
            {"$set": {"welcome_security.expire": message.text}},
        )
        await get_greetings_data.reset_cache(chat["chat_id"])
        await message.reply(
            strings["welcomesecurity_enabled:customized_time"].format(
                chat_name=chat["chat_title"],
                level=level,
                time=format_timedelta(
                    con_time, locale=strings["language_info"]["babel"]
                ),
            )
        )
    finally:
        await state.finish()


@register(
    cmds=["setsecuritynote", "sevesecuritynote"],
    user_admin=True,
    user_can_change_info=True,
)
@need_args_dec()
@chat_connection(admin=True, only_groups=True)
@get_strings_dec("greetings")
async def set_security_note(message, chat, strings):
    chat_id = chat["chat_id"]

    if message.get_args().lower().split()[0] in ["raw", "noformat"]:
        db_item = await get_greetings_data(chat_id)
        if "security_note" not in db_item:
            db_item = {"security_note": {}}
            db_item["security_note"]["text"] = strings["default_security_note"]
            db_item["security_note"]["parse_mode"] = "md"

        text, kwargs = await t_unparse_note_item(
            message, db_item["security_note"], chat_id, noformat=True
        )
        kwargs["reply_to"] = message.message_id

        await send_note(chat_id, text, **kwargs)
        return

    note = await get_parsed_note_list(message, split_args=-1)

    if (
        await db.greetings.update_one(
            {"chat_id": chat_id},
            {"$set": {"chat_id": chat_id, "security_note": note}},
            upsert=True,
        )
    ).modified_count > 0:
        await get_greetings_data.reset_cache(chat_id)
        text = strings["security_note_updated"]
    else:
        text = strings["security_note_saved"]

    await message.reply(text % chat["chat_title"])


@register(cmds="delsecuritynote", user_admin=True, user_can_change_info=True)
@chat_connection(admin=True, only_groups=True)
@get_strings_dec("greetings")
async def reset_security_note(message, chat, strings):
    chat_id = chat["chat_id"]

    if (
        await db.greetings.update_one(
            {"chat_id": chat_id}, {"$unset": {"security_note": 1}}, upsert=True
        )
    ).modified_count > 0:
        await get_greetings_data.reset_cache(chat_id)
        text = strings["security_note_updated"]
    else:
        text = strings["del_security_note_ok"]

    await message.reply(text % chat["chat_title"])


@register(only_groups=True, f="welcome")
@get_strings_dec("greetings")
async def welcome_security_handler(message: Message, strings):
    if len(message.new_chat_members) > 1:
        # FIXME: Daisy doesnt support adding multiple users currently
        return

    new_user = message.new_chat_members[0]
    chat_id = message.chat.id
    user_id = new_user.id

    if user_id == BOT_ID:
        await message.reply(strings["thank_for_add"])
        await bot.send_message(
            chat_id=LOGS_CHANNEL_ID,
            text=f"I was added to the group <b>{html.escape(message.chat.title)}</b> (<code>{message.chat.id}</code>)",
        )
        return

    db_item = await get_greetings_data(message.chat.id)
    if not db_item or "welcome_security" not in db_item:
        return

    if not await check_admin_rights(message, chat_id, BOT_ID, ["can_restrict_members"]):
        await message.reply(strings["not_admin_ws"])
        return

    user = await message.chat.get_member(user_id)
    # Check if user was muted before
    if user["status"] == "restricted":
        if user["can_send_messages"] is False:
            return

    # Check on OPs and chat owner
    if await is_user_admin(chat_id, user_id):
        return

    # check if user added is a bot
    if new_user.is_bot and await is_user_admin(chat_id, message.from_user.id):
        return

    if "security_note" not in db_item:
        db_item["security_note"] = {}
        db_item["security_note"]["text"] = strings["default_security_note"]
        db_item["security_note"]["parse_mode"] = "md"

    text, kwargs = await t_unparse_note_item(message, db_item["security_note"], chat_id)

    kwargs["reply_to"] = (
        None
        if "clean_service" in db_item and db_item["clean_service"]["enabled"] is True
        else message.message_id
    )

    kwargs["buttons"] = [] if not kwargs["buttons"] else kwargs["buttons"]
    kwargs["buttons"] += [
        Button.inline(strings["click_here"], f"ws_{chat_id}_{user_id}")
    ]

    # FIXME: Better workaround
    if not (msg := await send_note(chat_id, text, **kwargs)):
        # Wasn't able to sent message
        return

    # Mute user
    try:
        await mute_user(chat_id, user_id)
    except BadRequest as error:
        # TODO: Delete the "sent" message ^
        return await message.reply(f"welcome security failed due to {error.args[0]}")

    redis.set(f"welcome_security_users:{user_id}:{chat_id}", msg.id)

    if raw_time := db_item["welcome_security"].get("expire", None):
        time = convert_time(raw_time)
    else:
        time = convert_time(get_str_key("JOIN_CONFIRM_DURATION"))

    scheduler.add_job(
        join_expired,
        "date",
        id=f"wc_expire:{chat_id}:{user_id}",
        run_date=datetime.utcnow() + time,
        kwargs={
            "chat_id": chat_id,
            "user_id": user_id,
            "message_id": msg.id,
            "wlkm_msg_id": message.message_id,
        },
        replace_existing=True,
    )


async def join_expired(chat_id, user_id, message_id, wlkm_msg_id):
    user = await bot.get_chat_member(chat_id, user_id)
    if user.status != "restricted":
        return

    bot_user = await bot.get_chat_member(chat_id, BOT_ID)
    if (
        "can_restrict_members" not in bot_user
        or bot_user["can_restrict_members"] is False
    ):
        return

    key = "leave_silent:" + str(chat_id)
    redis.set(key, user_id)

    await unmute_user(chat_id, user_id)
    await kick_user(chat_id, user_id)
    await tbot.delete_messages(chat_id, [message_id, wlkm_msg_id])


@register(regexp=re.compile(r"ws_"), f="cb")
@get_strings_dec("greetings")
async def ws_redirecter(message, strings):
    payload = message.data.split("_")[1:]
    chat_id = int(payload[0])
    real_user_id = int(payload[1])
    called_user_id = message.from_user.id

    url = f"https://t.me/{BOT_USERNAME}?start=ws_{chat_id}_{called_user_id}_{message.message.message_id}"
    if not called_user_id == real_user_id:
        # The persons which are muted before wont have their signatures registered on cache
        if not redis.exists(f"welcome_security_users:{called_user_id}:{chat_id}"):
            await message.answer(strings["not_allowed"], show_alert=True)
            return
        else:
            # For those who lost their buttons
            url = f"https://t.me/{BOT_USERNAME}?start=ws_{chat_id}_{called_user_id}_{message.message.message_id}_0"
    await message.answer(url=url)


@register(CommandStart(re.compile(r"ws_")), allow_kwargs=True)
@get_strings_dec("greetings")
async def welcome_security_handler_pm(
    message: Message, strings, regexp=None, state=None, **kwargs
):
    args = message.get_args().split("_")
    chat_id = int(args[1])

    async with state.proxy() as data:
        data["chat_id"] = chat_id
        data["msg_id"] = int(args[3])
        data["to_delete"] = bool(int(args[4])) if len(args) > 4 else True

    db_item = await get_greetings_data(chat_id)

    level = db_item["welcome_security"]["level"]

    if level == "button":
        await WelcomeSecurityState.button.set()
        await send_button(message, state)

    elif level == "math":
        await WelcomeSecurityState.math.set()
        await send_btn_math(message, state)

    elif level == "captcha":
        await WelcomeSecurityState.captcha.set()
        await send_captcha(message, state)


@get_strings_dec("greetings")
async def send_button(message, state, strings):
    text = strings["btn_button_text"]
    buttons = InlineKeyboardMarkup().add(
        InlineKeyboardButton(strings["click_here"], callback_data="wc_button_btn")
    )
    verify_msg_id = (await message.reply(text, reply_markup=buttons)).message_id
    async with state.proxy() as data:
        data["verify_msg_id"] = verify_msg_id


@register(
    regexp="wc_button_btn", f="cb", state=WelcomeSecurityState.button, allow_kwargs=True
)
async def wc_button_btn_cb(event, state=None, **kwargs):
    await welcome_security_passed(event, state)


def generate_captcha(number=None):
    if not number:
        number = str(random.randint(10001, 99999))
    captcha = ImageCaptcha(fonts=ALL_FONTS, width=200, height=100).generate_image(
        number
    )
    img = io.BytesIO()
    captcha.save(img, "PNG")
    img.seek(0)
    return img, number


@get_strings_dec("greetings")
async def send_captcha(message, state, strings):
    img, num = generate_captcha()
    async with state.proxy() as data:
        data["captcha_num"] = num
    text = strings["ws_captcha_text"].format(
        user=await get_user_link(message.from_user.id)
    )

    buttons = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            strings["regen_captcha_btn"], callback_data="regen_captcha"
        )
    )

    verify_msg_id = (
        await message.answer_photo(img, caption=text, reply_markup=buttons)
    ).message_id
    async with state.proxy() as data:
        data["verify_msg_id"] = verify_msg_id


@register(
    regexp="regen_captcha",
    f="cb",
    state=WelcomeSecurityState.captcha,
    allow_kwargs=True,
)
@get_strings_dec("greetings")
async def change_captcha(event, strings, state=None, **kwargs):
    message = event.message
    async with state.proxy() as data:
        data["regen_num"] = 1 if "regen_num" not in data else data["regen_num"] + 1
        regen_num = data["regen_num"]

        if regen_num > 3:
            img, num = generate_captcha(number=data["captcha_num"])
            text = strings["last_chance"]
            await message.edit_media(InputMediaPhoto(img, caption=text))
            return

        img, num = generate_captcha()
        data["captcha_num"] = num

    text = strings["ws_captcha_text"].format(
        user=await get_user_link(event.from_user.id)
    )

    buttons = InlineKeyboardMarkup().add(
        InlineKeyboardButton(
            strings["regen_captcha_btn"], callback_data="regen_captcha"
        )
    )

    await message.edit_media(InputMediaPhoto(img, caption=text), reply_markup=buttons)


@register(f="text", state=WelcomeSecurityState.captcha, allow_kwargs=True)
@get_strings_dec("greetings")
async def check_captcha_text(message, strings, state=None, **kwargs):
    num = message.text.split(" ")[0]

    if not num.isdigit():
        await message.reply(strings["num_is_not_digit"])
        return

    async with state.proxy() as data:
        captcha_num = data["captcha_num"]

    if int(num) != int(captcha_num):
        await message.reply(strings["bad_num"])
        return

    await welcome_security_passed(message, state)


# Btns


def gen_expression():
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    if random.getrandbits(1):
        while a < b:
            b = random.randint(1, 10)
        answr = a - b
        expr = f"{a} - {b}"
    else:
        b = random.randint(1, 10)

        answr = a + b
        expr = f"{a} + {b}"

    return expr, answr


def gen_int_btns(answer):
    buttons = []

    for a in [random.randint(1, 20) for _ in range(3)]:
        while a == answer:
            a = random.randint(1, 20)
        buttons.append(Button.inline(str(a), data="wc_int_btn:" + str(a)))

    buttons.insert(
        random.randint(0, 3),
        Button.inline(str(answer), data="wc_int_btn:" + str(answer)),
    )

    return buttons


@get_strings_dec("greetings")
async def send_btn_math(message, state, strings, msg_id=False):
    chat_id = message.chat.id
    expr, answer = gen_expression()

    async with state.proxy() as data:
        data["num"] = answer

    btns = gen_int_btns(answer)

    if msg_id:
        async with state.proxy() as data:
            data["last"] = True
        text = strings["math_wc_rtr_text"] + strings["btn_wc_text"] % expr
    else:
        text = strings["btn_wc_text"] % expr
        msg_id = (await message.reply(text)).message_id

    async with state.proxy() as data:
        data["verify_msg_id"] = msg_id

    # TODO: change to aiogram
    await tbot.edit_message(chat_id, msg_id, text, buttons=btns)


@register(
    regexp="wc_int_btn:", f="cb", state=WelcomeSecurityState.math, allow_kwargs=True
)
@get_strings_dec("greetings")
async def wc_math_check_cb(event, strings, state=None, **kwargs):
    num = int(event.data.split(":")[1])

    async with state.proxy() as data:
        answer = data["num"]
        if "last" in data:
            await state.finish()
            await event.answer(strings["math_wc_sry"], show_alert=True)
            await event.message.delete()
            return

    if not num == answer:
        await send_btn_math(event.message, state, msg_id=event.message.message_id)
        await event.answer(strings["math_wc_wrong"], show_alert=True)
        return

    await welcome_security_passed(event, state)


@get_strings_dec("greetings")
async def welcome_security_passed(
    message: Union[CallbackQuery, Message], state, strings
):
    user_id = message.from_user.id
    async with state.proxy() as data:
        chat_id = data["chat_id"]
        msg_id = data["msg_id"]
        verify_msg_id = data["verify_msg_id"]
        to_delete = data["to_delete"]

    with suppress(ChatAdminRequired):
        await unmute_user(chat_id, user_id)

    with suppress(MessageToDeleteNotFound, MessageCantBeDeleted):
        if to_delete:
            await bot.delete_message(chat_id, msg_id)
        await bot.delete_message(user_id, verify_msg_id)
    await state.finish()

    with suppress(MessageToDeleteNotFound, MessageCantBeDeleted):
        message_id = redis.get(f"welcome_security_users:{user_id}:{chat_id}")
        # Delete the person's real security button if exists!
        if message_id:
            await bot.delete_message(chat_id, message_id)

    redis.delete(f"welcome_security_users:{user_id}:{chat_id}")

    with suppress(JobLookupError):
        scheduler.remove_job(f"wc_expire:{chat_id}:{user_id}")

    title = (await db.chat_list.find_one({"chat_id": chat_id}))["chat_title"]

    if "data" in message:
        await message.answer(strings["passed_no_frm"] % title, show_alert=True)
    else:
        await message.reply(strings["passed"] % title)

    db_item = await get_greetings_data(chat_id)

    if "message" in message:
        message = message.message

    # Welcome
    if "note" in db_item and not db_item.get("welcome_disabled", False):
        text, kwargs = await t_unparse_note_item(
            message.reply_to_message
            if message.reply_to_message is not None
            else message,
            db_item["note"],
            chat_id,
        )
        await send_note(user_id, text, **kwargs)

    # Welcome mute
    if "welcome_mute" in db_item and db_item["welcome_mute"]["enabled"] is not False:
        user = await bot.get_chat_member(chat_id, user_id)
        if "can_send_messages" not in user or user["can_send_messages"] is True:
            await restrict_user(
                chat_id,
                user_id,
                until_date=convert_time(db_item["welcome_mute"]["time"]),
            )

    chat = await db.chat_list.find_one({"chat_id": chat_id})

    buttons = None
    if chat_nick := chat["chat_nick"] if chat.get("chat_nick", None) else None:
        buttons = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text=strings["click_here"], url=f"t.me/{chat_nick}")
        )

    await bot.send_message(user_id, strings["verification_done"], reply_markup=buttons)


# End Welcome Security

# Welcomes
@register(only_groups=True, f="welcome")
@get_strings_dec("greetings")
async def welcome_trigger(message: Message, strings):
    if len(message.new_chat_members) > 1:
        # FIXME: Daisy doesnt support adding multiple users currently
        return

    chat_id = message.chat.id
    user_id = message.new_chat_members[0].id

    if user_id == BOT_ID:
        return

    if not (db_item := await get_greetings_data(message.chat.id)):
        db_item = {}

    if "welcome_disabled" in db_item and db_item["welcome_disabled"] is True:
        return

    if "welcome_security" in db_item and db_item["welcome_security"]["enabled"]:
        return

    # Welcome
    if "note" not in db_item:
        db_item["note"] = {"text": strings["default_welcome"], "parse_mode": "md"}
    reply_to = (
        message.message_id
        if "clean_welcome" in db_item
        and db_item["clean_welcome"]["enabled"] is not False
        else None
    )
    text, kwargs = await t_unparse_note_item(message, db_item["note"], chat_id)
    msg = await send_note(chat_id, text, reply_to=reply_to, **kwargs)
    # Clean welcome
    if "clean_welcome" in db_item and db_item["clean_welcome"]["enabled"] is not False:
        if value := redis.get(_clean_welcome.format(chat=chat_id)):
            with suppress(MessageToDeleteNotFound, MessageCantBeDeleted):
                await bot.delete_message(chat_id, value)
        redis.set(_clean_welcome.format(chat=chat_id), msg.id)

    # Welcome mute
    if user_id == BOT_ID:
        return
    if "welcome_mute" in db_item and db_item["welcome_mute"]["enabled"] is not False:
        user = await bot.get_chat_member(chat_id, user_id)
        if "can_send_messages" not in user or user["can_send_messages"] is True:
            if not await check_admin_rights(
                message, chat_id, BOT_ID, ["can_restrict_members"]
            ):
                await message.reply(strings["not_admin_wm"])
                return

            await restrict_user(
                chat_id,
                user_id,
                until_date=convert_time(db_item["welcome_mute"]["time"]),
            )


# Clean service trigger
@register(only_groups=True, f="service")
@get_strings_dec("greetings")
async def clean_service_trigger(message, strings):
    chat_id = message.chat.id

    if message.new_chat_members[0].id == BOT_ID:
        return

    if not (db_item := await get_greetings_data(chat_id)):
        return

    if "clean_service" not in db_item or db_item["clean_service"]["enabled"] is False:
        return

    if not await check_admin_rights(message, chat_id, BOT_ID, ["can_delete_messages"]):
        await bot.send_message(chat_id, strings["not_admin_wsr"])
        return

    with suppress(MessageToDeleteNotFound, MessageCantBeDeleted):
        await message.delete()


_clean_welcome = "cleanwelcome:{chat}"


@cached()
async def get_greetings_data(chat: int) -> Optional[dict]:
    return await db.greetings.find_one({"chat_id": chat})


async def __export__(chat_id):
    if greetings := await get_greetings_data(chat_id):
        del greetings["_id"]
        del greetings["chat_id"]

        return {"greetings": greetings}


async def __import__(chat_id, data):
    await db.greetings.update_one({"chat_id": chat_id}, {"$set": data}, upsert=True)
    await get_greetings_data.reset_cache(chat_id)


__mod_name__ = "Greetings"

__help__ = """
<b>Available commands:</b>
<b>General:</b>
- /setwelcome or /savewelcome: Set welcome
- /setwelcome (on/off): Disable/enabled welcomes in your chat
- /welcome: Shows current welcomes settings and welcome text
- /resetwelcome: Reset welcomes settings

<b>Welcome security:</b>
- /welcomesecurity (level)
Turns on welcome security with specified level, either button or captcha.
Setting up welcome security will give you a choice to customize join expiration time aka minimum time given to user to verify themselves not a bot, users who do not verify within this time would be kicked!

- /welcomesecurity (off/no/0): Disable welcome security
- /setsecuritynote: Customise the "Please press button below to verify themself as human!" text
- /delsecuritynote: Reset security text to defaults

<b>Available levels:</b>
- <code>button</code>: Ask user to press "I'm not a bot" button
- <code>math</code>: Asking to solve simple math query, few buttons with answers will be provided, only one will have right answer
- <code>captcha</code>: Ask user to enter captcha

<b>Welcome mutes:</b>
- /welcomemute (time): Set welcome mute (no media) for X time
- /welcomemute (off/no): Disable welcome mute

<b>Purges:</b>
- /cleanwelcome (on/off): Deletes old welcome messages and last one after 45 mintes
- /cleanservice (on/off): Cleans service messages (user X joined)

If welcome security is enabled, user will be welcomed with security text, if user successfully verify self as user, he/she will be welcomed also with welcome text in his PM (to prevent spamming in chat).

If user didn't verified self for 24 hours he/she will be kicked from chat.

<b>Addings buttons and variables to welcomes or security text:</b>
Buttons and variables syntax is same as notes buttons and variables.
Send /buttonshelp and /variableshelp to get started with using it.

<b>Settings images, gifs, videos or stickers as welcome:</b>
Saving attachments on welcome is same as saving notes with it, read the notes help about it. But keep in mind what you have to replace /save to /setwelcome

<b>Examples:</b>
<code>- Get the welcome message without any formatting
-> /welcome raw</code>

<b> Good Bye </b>
 - /setgoodbye [reply to a text]: Saves the message as a goodbye note in the chat.
 - /checkgoodbye: Check whether you have a goodbye note in the chat.
 - /cleargoodbye: Deletes the goodbye note for the current chat.
 - /cleangoodbye [on/off]: Clean previous goodbye message before farewelling a user.
"""
