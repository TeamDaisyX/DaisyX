# Copyright (C) 2021 ProgrammingError

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

import github  # pyGithub
from pyrogram import filters

from DaisyX.services.pyrogram import pbot as client


@client.on_message(filters.command("contributors") & ~filters.edited)
async def give_cobtribs(c, m):
    g = github.Github()
    repo = g.get_repo("TeamDaisyX/DaisyX")
    co = "".join(
        f"{n}. [{i.login}](https://github.com/{i.login})\n"
        for n, i in enumerate(repo.get_contributors(), start=1)
    )

    t = f"**DaisyX Contributors**\n\n{co}"
    await m.reply(t, disable_web_page_preview=True)
