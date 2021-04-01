import io
import time

import aiohttp
from telethon.tl import functions, types
from telethon.tl.types import *

from DaisyX.config import get_str_key

OPENWEATHERMAP_ID = get_str_key("OPENWEATHERMAP_ID", "")
from DaisyX.services.events import register
from DaisyX.services.telethon import tbot


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await tbot(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerChat):
        ui = await tbot.get_peer_id(user)
        ps = (
            await tbot(functions.messages.GetFullChatRequest(chat.chat_id))
        ).full_chat.participants.participants
        return isinstance(
            next((p for p in ps if p.user_id == ui), None),
            (types.ChatParticipantAdmin, types.ChatParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


@register(pattern="^/weather (.*)")
async def _(event):
    if event.fwd_from:
        return
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    sample_url = (
        "https://api.openweathermap.org/data/2.5/weather?q={}&APPID={}&units=metric"
    )
    input_str = event.pattern_match.group(1)
    async with aiohttp.ClientSession() as session:
        response_api_zero = await session.get(
            sample_url.format(input_str, OPENWEATHERMAP_ID)
        )
    response_api = await response_api_zero.json()
    if response_api["cod"] == 200:
        country_code = response_api["sys"]["country"]
        country_time_zone = int(response_api["timezone"])
        sun_rise_time = int(response_api["sys"]["sunrise"]) + country_time_zone
        sun_set_time = int(response_api["sys"]["sunset"]) + country_time_zone
        await event.reply(
            """**Location**: {}
**Temperature ☀️**: {}°С
    __minimium__: {}°С
    __maximum__ : {}°С
**Humidity 🌤**: {}%
**Wind** 💨: {}m/s
**Clouds** ☁️: {}hpa
**Sunrise** 🌤: {} {}
**Sunset** 🌝: {} {}""".format(
                input_str,
                response_api["main"]["temp"],
                response_api["main"]["temp_min"],
                response_api["main"]["temp_max"],
                response_api["main"]["humidity"],
                response_api["wind"]["speed"],
                response_api["clouds"]["all"],
                # response_api["main"]["pressure"],
                time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(sun_rise_time)),
                country_code,
                time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(sun_set_time)),
                country_code,
            )
        )
    else:
        await event.reply(response_api["message"])


@register(pattern="^/weatherimg (.*)")
async def _(event):
    if event.fwd_from:
        return
    if event.is_group:
        if await is_register_admin(event.input_chat, event.message.sender_id):
            pass
        elif event.chat_id == iid and event.sender_id == userss:
            pass
        else:
            return
    sample_url = "https://wttr.in/{}.png"
    # logger.info(sample_url)
    input_str = event.pattern_match.group(1)
    async with aiohttp.ClientSession() as session:
        response_api_zero = await session.get(sample_url.format(input_str))
        # logger.info(response_api_zero)
        response_api = await response_api_zero.read()
        with io.BytesIO(response_api) as out_file:
            await event.reply(file=out_file)
