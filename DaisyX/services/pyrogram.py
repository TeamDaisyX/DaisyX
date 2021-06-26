# This file is part of DaisyXBot (Telegram Bot)

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
import logging

from pyrogram import Client

# from pyromod import listen
from DaisyX.config import get_int_key, get_str_key

TOKEN = get_str_key("TOKEN", required=True)
APP_ID = get_int_key("APP_ID", required=True)
APP_HASH = get_str_key("APP_HASH", required=True)
session_name = TOKEN.split(":")[0]
pbot = Client(
    session_name,
    api_id=APP_ID,
    api_hash=APP_HASH,
    bot_token=TOKEN,
)

# disable logging for pyrogram [not for ERROR logging]
logging.getLogger("pyrogram").setLevel(level=logging.ERROR)

pbot.start()
