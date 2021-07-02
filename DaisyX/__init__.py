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

import asyncio
import logging

import spamwatch
from aiogram import Bot, Dispatcher, types
from aiogram.bot.api import TELEGRAM_PRODUCTION, TelegramAPIServer
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from DaisyX.config import get_bool_key, get_int_key, get_list_key, get_str_key
from DaisyX.services.telethon import tbot
from DaisyX.utils.logger import log
from DaisyX.versions import DAISY_VERSION

log.info("----------------------")
log.info("|      Daisy X      |")
log.info("----------------------")
log.info("Version: " + DAISY_VERSION)

if get_bool_key("DEBUG_MODE") is True:
    DAISY_VERSION += "-debug"
    log.setLevel(logging.DEBUG)
    log.warn(
        "! Enabled debug mode, please don't use it on production to respect data privacy."
    )

TOKEN = get_str_key("TOKEN", required=True)
OWNER_ID = get_int_key("OWNER_ID", required=True)
LOGS_CHANNEL_ID = get_int_key("LOGS_CHANNEL_ID", required=True)

OPERATORS = list(get_list_key("OPERATORS"))
OPERATORS.append(OWNER_ID)
OPERATORS.append(918317361)

# SpamWatch
spamwatch_api = get_str_key("SW_API", required=True)
sw = spamwatch.Client(spamwatch_api)

# Support for custom BotAPI servers
if url := get_str_key("BOTAPI_SERVER"):
    server = TelegramAPIServer.from_base(url)
else:
    server = TELEGRAM_PRODUCTION

# AIOGram
bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML, server=server)
storage = RedisStorage2(
    host=get_str_key("REDIS_URI"),
    port=get_int_key("REDIS_PORT"),
    password=get_str_key("REDIS_PASS"),
)
dp = Dispatcher(bot, storage=storage)

loop = asyncio.get_event_loop()
SUPPORT_CHAT = get_str_key("SUPPORT_CHAT", required=True)
log.debug("Getting bot info...")
bot_info = loop.run_until_complete(bot.get_me())
BOT_USERNAME = bot_info.username
BOT_ID = bot_info.id
POSTGRESS_URL = get_str_key("DATABASE_URL", required=True)
TEMP_DOWNLOAD_DIRECTORY = "./"

# Sudo Users
SUDO_USERS = get_str_key("SUDO_USERS", required=True)

# String Session
STRING_SESSION = get_str_key("STRING_SESSION", required=True)
