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

import time
from importlib import import_module

from aiogram import types
from aiogram.dispatcher.handler import SkipHandler
from sentry_sdk import configure_scope

from DaisyX import BOT_USERNAME, dp
from DaisyX.config import get_bool_key
from DaisyX.modules.error import parse_update
from DaisyX.utils.filters import ALL_FILTERS
from DaisyX.utils.logger import log

DEBUG_MODE = get_bool_key("DEBUG_MODE")
ALLOW_F_COMMANDS = get_bool_key("ALLOW_FORWARDS_COMMANDS")
ALLOW_COMMANDS_FROM_EXC = get_bool_key("ALLOW_COMMANDS_WITH_!")
CMD_NOT_MONO = get_bool_key("DISALLOW_MONO_CMDS")

REGISTRED_COMMANDS = []
COMMANDS_ALIASES = {}

# Import filters
log.info("Filters to load: %s", str(ALL_FILTERS))
for module_name in ALL_FILTERS:
    log.debug("Importing " + module_name)
    imported_module = import_module("DaisyX.utils.filters." + module_name)
log.info("Filters loaded!")


def register(*args, cmds=None, f=None, allow_edited=True, allow_kwargs=False, **kwargs):
    if cmds and type(cmds) is str:
        cmds = [cmds]

    register_kwargs = {}

    if cmds and not f:
        regex = r"\A^{}(".format("[!/]" if ALLOW_COMMANDS_FROM_EXC else "/")

        if "not_forwarded" not in kwargs and ALLOW_F_COMMANDS is False:
            kwargs["not_forwarded"] = True

        if "cmd_not_mono" not in kwargs and CMD_NOT_MONO:
            kwargs["cmd_not_mono"] = True

        for idx, cmd in enumerate(cmds):
            if cmd in REGISTRED_COMMANDS:
                log.warn(f"Duplication of /{cmd} command")
            REGISTRED_COMMANDS.append(cmd)
            regex += cmd

            if not idx == len(cmds) - 1:
                if not cmds[0] in COMMANDS_ALIASES:
                    COMMANDS_ALIASES[cmds[0]] = [cmds[idx + 1]]
                else:
                    COMMANDS_ALIASES[cmds[0]].append(cmds[idx + 1])
                regex += "|"

        if "disable_args" in kwargs:
            del kwargs["disable_args"]
            regex += f")($|@{BOT_USERNAME}$)"
        else:
            regex += f")(|@{BOT_USERNAME})(:? |$)"

        register_kwargs["regexp"] = regex

    elif f == "text":
        register_kwargs["content_types"] = types.ContentTypes.TEXT

    elif f == "welcome":
        register_kwargs["content_types"] = types.ContentTypes.NEW_CHAT_MEMBERS

    elif f == "leave":
        register_kwargs["content_types"] = types.ContentTypes.LEFT_CHAT_MEMBER

    elif f == "service":
        register_kwargs["content_types"] = types.ContentTypes.NEW_CHAT_MEMBERS
    elif f == "any":
        register_kwargs["content_types"] = types.ContentTypes.ANY

    log.debug(f"Registred new handler: <d><n>{str(register_kwargs)}</></>")

    register_kwargs.update(kwargs)

    def decorator(func):
        async def new_func(*def_args, **def_kwargs):
            message = def_args[0]

            if cmds:
                message.conf["cmds"] = cmds

            if allow_kwargs is False:
                def_kwargs = dict()

            with configure_scope() as scope:
                parsed_update = parse_update(dict(message))
                scope.set_extra("update", str(parsed_update))

            if DEBUG_MODE:
                # log.debug('[*] Starting {}.'.format(func.__name__))
                # log.debug('Event: \n' + str(message))
                start = time.time()
                await func(*def_args, **def_kwargs)
                log.debug(
                    "[*] {} Time: {} sec.".format(func.__name__, time.time() - start)
                )
            else:
                await func(*def_args, **def_kwargs)
            raise SkipHandler()

        if f == "cb":
            dp.register_callback_query_handler(new_func, *args, **register_kwargs)
        else:
            dp.register_message_handler(new_func, *args, **register_kwargs)
            if allow_edited is True:
                dp.register_edited_message_handler(new_func, *args, **register_kwargs)

    return decorator
