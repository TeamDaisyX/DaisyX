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

import httpx
import rapidjson as json

# This file is an adaptation / port from the Galaxy Helper Bot.
# Copyright (C) KassemSYR. All rights reserved.


class GetDevice:
    def __init__(self, device):
        """Get device info by codename or model!"""
        self.device = device

    async def get(self):
        if self.device.lower().startswith("sm-"):
            async with httpx.AsyncClient(http2=True) as http:
                data = await http.get(
                    "https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_model.json"
                )
                db = json.loads(data.content)
                await http.aclose()
            try:
                name = db[self.device.upper()][0]["name"]
                device = db[self.device.upper()][0]["device"]
                brand = db[self.device.upper()][0]["brand"]
                model = self.device.lower()
                return {"name": name, "device": device, "model": model, "brand": brand}
            except KeyError:
                return False
        else:
            async with httpx.AsyncClient(http2=True) as http:
                data = await http.get(
                    "https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_device.json"
                )
                db = json.loads(data.content)
                await http.aclose()
            newdevice = (
                self.device.strip("lte").lower()
                if self.device.startswith("beyond")
                else self.device.lower()
            )
            try:
                name = db[newdevice][0]["name"]
                model = db[newdevice][0]["model"]
                brand = db[newdevice][0]["brand"]
                device = self.device.lower()
                return {"name": name, "device": device, "model": model, "brand": brand}
            except KeyError:
                return False
