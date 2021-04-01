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

import os

import yaml
from babel.core import Locale

from DaisyX.services.mongo import db
from DaisyX.services.redis import redis
from DaisyX.utils.logger import log

LANGUAGES = {}

log.info("Loading localizations...")

for filename in os.listdir("DaisyX/localization"):
    log.debug("Loading language file " + filename)
    with open("DaisyX/localization/" + filename, "r", encoding="utf8") as f:
        lang = yaml.load(f, Loader=yaml.CLoader)

        lang_code = lang["language_info"]["code"]
        lang["language_info"]["babel"] = Locale(lang_code)

        LANGUAGES[lang_code] = lang

log.info(
    "Languages loaded: {}".format(
        [
            language["language_info"]["babel"].display_name
            for language in LANGUAGES.values()
        ]
    )
)


async def get_chat_lang(chat_id):
    r = redis.get("lang_cache_{}".format(chat_id))
    if r:
        return r
    else:
        db_lang = await db.lang.find_one({"chat_id": chat_id})
        if db_lang:
            # Rebuild lang cache
            redis.set("lang_cache_{}".format(chat_id), db_lang["lang"])
            return db_lang["lang"]
        user_lang = await db.user_list.find_one({"user_id": chat_id})
        if user_lang and user_lang["user_lang"] in LANGUAGES:
            # Add telegram language in lang cache
            redis.set("lang_cache_{}".format(chat_id), user_lang["user_lang"])
            return user_lang["user_lang"]
        else:
            return "en"


async def change_chat_lang(chat_id, lang):
    redis.set("lang_cache_{}".format(chat_id), lang)
    await db.lang.update_one(
        {"chat_id": chat_id}, {"$set": {"chat_id": chat_id, "lang": lang}}, upsert=True
    )


async def get_strings(chat_id, module, mas_name="STRINGS"):
    chat_lang = await get_chat_lang(chat_id)
    if chat_lang not in LANGUAGES:
        await change_chat_lang(chat_id, "en")

    class Strings:
        @staticmethod
        def get_strings(lang, mas_name, module):

            if (
                mas_name not in LANGUAGES[lang]
                or module not in LANGUAGES[lang][mas_name]
            ):
                return {}

            data = LANGUAGES[lang][mas_name][module]

            if mas_name == "STRINGS":
                data["language_info"] = LANGUAGES[chat_lang]["language_info"]
            return data

        def get_string(self, name):
            data = self.get_strings(chat_lang, mas_name, module)
            if name not in data:
                data = self.get_strings("en", mas_name, module)

            return data[name]

        def __getitem__(self, key):
            return self.get_string(key)

    return Strings()


async def get_string(chat_id, module, name, mas_name="STRINGS"):
    strings = await get_strings(chat_id, module, mas_name=mas_name)
    return strings[name]


def get_strings_dec(module, mas_name="STRINGS"):
    def wrapped(func):
        async def wrapped_1(*args, **kwargs):
            message = args[0]
            if hasattr(message, "chat"):
                chat_id = message.chat.id
            elif hasattr(message, "message"):
                chat_id = message.message.chat.id
            else:
                chat_id = None

            strings = await get_strings(chat_id, module, mas_name=mas_name)
            return await func(*args, strings, **kwargs)

        return wrapped_1

    return wrapped


async def get_chat_lang_info(chat_id):
    chat_lang = await get_chat_lang(chat_id)
    return LANGUAGES[chat_lang]["language_info"]
