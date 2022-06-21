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
import os
from importlib import import_module

from aiogram import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from DaisyX import TOKEN, bot, dp
from DaisyX.config import get_bool_key, get_list_key
from DaisyX.modules import ALL_MODULES, LOADED_MODULES, MOD_HELP
from DaisyX.utils.logger import log

if get_bool_key("DEBUG_MODE"):
    log.debug("Enabling logging middleware.")
    dp.middleware.setup(LoggingMiddleware())

LOAD = get_list_key("LOAD")
DONT_LOAD = get_list_key("DONT_LOAD")

if get_bool_key("LOAD_MODULES"):
    modules = LOAD if len(LOAD) > 0 else ALL_MODULES
    modules = [x for x in modules if x not in DONT_LOAD]

    log.info("Modules to load: %s", str(modules))
    for module_name in modules:
        # Load pm_menu at last
        if module_name == "pm_menu":
            continue
        log.debug(f"Importing <d><n>{module_name}</></>")
        imported_module = import_module(f"DaisyX.modules.{module_name}")
        if hasattr(imported_module, "__help__"):
            if hasattr(imported_module, "__mod_name__"):
                MOD_HELP[imported_module.__mod_name__] = imported_module.__help__
            else:
                MOD_HELP[imported_module.__name__] = imported_module.__help__
        LOADED_MODULES.append(imported_module)
    log.info("Modules loaded!")
else:
    log.warning("Not importing modules!")

loop = asyncio.get_event_loop()

import_module("DaisyX.modules.pm_menu")
# Import misc stuff
import_module("DaisyX.utils.exit_gracefully")
if not get_bool_key("DEBUG_MODE"):
    import_module("DaisyX.utils.sentry")


async def before_srv_task(loop):
    for module in [m for m in LOADED_MODULES if hasattr(m, "__before_serving__")]:
        log.debug(f"Before serving: {module.__name__}")
        loop.create_task(module.__before_serving__(loop))


async def start(_):
    log.debug("Starting before serving task for all modules...")
    loop.create_task(before_srv_task(loop))

    if not get_bool_key("DEBUG_MODE"):
        log.debug("Waiting 2 seconds...")
        await asyncio.sleep(2)


async def start_webhooks(_):
    url = os.getenv("WEBHOOK_URL") + f"/{TOKEN}"
    await bot.set_webhook(url)
    return await start(_)


log.info("Starting loop..")
log.info("Aiogram: Using polling method")

if os.getenv("WEBHOOKS", False):
    port = os.getenv("WEBHOOKS_PORT", 8080)
    executor.start_webhook(dp, f"/{TOKEN}", on_startup=start_webhooks, port=port)
else:
    executor.start_polling(
        dp,
        loop=loop,
        on_startup=start,
        timeout=15,
        relax=0.1,
        fast=True,
        skip_updates=True,
    )
