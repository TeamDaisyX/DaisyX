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
import sys

import yaml
from envparse import env

from DaisyX.utils.logger import log

DEFAULTS = {
    "LOAD_MODULES": True,
    "DEBUG_MODE": True,
    "REDIS_HOST": "localhost",
    "REDIS_PORT": 6379,
    "REDIS_DB_FSM": 1,
    "MONGODB_URI": "localhost",
    "MONGO_DB": "DaisyX",
    "API_PORT": 8080,
    "JOIN_CONFIRM_DURATION": "30m",
}

CONFIG_PATH = "data/bot_conf.yaml"
if os.name == "nt":
    log.debug("Detected Windows, changing config path...")
    CONFIG_PATH = os.getcwd() + "\\data\\bot_conf.yaml"

if os.path.isfile(CONFIG_PATH):
    log.info(CONFIG_PATH)
    for item in (
        data := yaml.load(open("data/bot_conf.yaml", "r"), Loader=yaml.CLoader)
    ):
        DEFAULTS[item.upper()] = data[item]
else:
    log.info("Using env vars")


def get_str_key(name, required=False):
    default = DEFAULTS[name] if name in DEFAULTS else None
    if not (data := env.str(name, default=default)) and not required:
        log.warn(f"No str key: {name}")
        return None
    elif not data:
        log.critical(f"No str key: {name}")
        sys.exit(2)
    else:
        return data


def get_int_key(name, required=False):
    default = DEFAULTS[name] if name in DEFAULTS else None
    if not (data := env.int(name, default=default)) and not required:
        log.warn(f"No int key: {name}")
        return None
    elif not data:
        log.critical(f"No int key: {name}")
        sys.exit(2)
    else:
        return data


def get_list_key(name, required=False):
    default = DEFAULTS[name] if name in DEFAULTS else None
    if not (data := env.list(name, default=default)) and not required:
        log.warn(f"No list key: {name}")
        return []
    elif not data:
        log.critical(f"No list key: {name}")
        sys.exit(2)
    else:
        return data


def get_bool_key(name, required=False):
    default = DEFAULTS[name] if name in DEFAULTS else None
    if not (data := env.bool(name, default=default)) and not required:
        log.warn(f"No bool key: {name}")
        return False
    elif not data:
        log.critical(f"No bool key: {name}")
        sys.exit(2)
    else:
        return data
