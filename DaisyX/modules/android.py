# Copyright (C) 2018 - 2020 MrYacha. All rights reserved. Source code available under the AGPL.
# Copyright (C) 2021 TeamDaisyX
# Copyright (C) 2020 Inuka Asith

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

import httpx
import rapidjson as json
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bs4 import BeautifulSoup

from DaisyX import decorator
from DaisyX.decorator import register

from .utils.android import GetDevice
from .utils.disable import disableable_dec
from .utils.message import get_arg, get_cmd

MIUI_FIRM = "https://raw.githubusercontent.com/XiaomiFirmwareUpdater/miui-updates-tracker/master/data/latest.yml"
REALME_FIRM = "https://raw.githubusercontent.com/RealmeUpdater/realme-updates-tracker/master/data/latest.yml"


@register(cmds="whatis")
@disableable_dec("whatis")
async def whatis(message):
    device = get_arg(message)
    if not device:
        m = "Please write your codename into it, i.e <code>/whatis raphael</code>"
        await message.reply(m)
        return

    data = await GetDevice(device).get()
    if data:
        name = data["name"]
        device = data["device"]
        brand = data["brand"]
        data["model"]
    else:
        m = "coudn't find your device, check device & try!"
        await message.reply(m)
        return

    m = f"<b>{device}</b> is <code>{brand} {name}</code>\n"
    await message.reply(m)


@decorator.register(cmds=["models", "variants"])
@disableable_dec("models")
async def variants(message):
    device = get_arg(message)
    if not device:
        m = "Please write your codename into it, i.e <code>/specs herolte</code>"
        await message.reply(m)
        return

    data = await GetDevice(device).get()
    if data:
        name = data["name"]
        device = data["device"]
    else:
        m = "coudn't find your device, chack device & try!"
        await message.reply(m)
        return

    async with httpx.AsyncClient(http2=True) as http:
        data = await http.get(
            "https://raw.githubusercontent.com/androidtrackers/certified-android-devices/master/by_device.json"
        )
        db = json.loads(data.content)
    device = db[device]
    m = f"<b>{name}</b> variants:\n\n"

    for i in device:
        name = i["name"]
        model = i["model"]
        m += "<b>Model</b>: <code>{}</code> \n<b>Name:</b> <code>{}</code>\n\n".format(
            model, name
        )

    await http.aclose()
    await message.reply(m)


@register(cmds="magisk")
@disableable_dec("magisk")
async def magisk(message):
    url = "https://raw.githubusercontent.com/topjohnwu/magisk_files/"
    releases = "<b>Latest Magisk Releases:</b>\n"
    variant = ["master/stable", "master/beta", "canary/canary"]
    for variants in variant:
        async with httpx.AsyncClient(http2=True) as http:
            fetch = await http.get(url + variants + ".json")
            data = json.loads(fetch.content)
        if variants == "master/stable":
            name = "<b>Stable</b>"
            cc = 0
            branch = "master"
        elif variants == "master/beta":
            name = "<b>Beta</b>"
            cc = 0
            branch = "master"
        elif variants == "canary/canary":
            name = "<b>Canary</b>"
            cc = 1
            branch = "canary"

        if variants == "canary/canary":
            releases += f'{name}: <a href="{url}{branch}/{data["magisk"]["link"]}">v{data["magisk"]["version"]}</a> (<code>{data["magisk"]["versionCode"]}</code>) | '
        else:
            releases += f'{name}: <a href="{data["magisk"]["link"]}">v{data["magisk"]["version"]}</a> (<code>{data["magisk"]["versionCode"]}</code>) | '

        if cc == 1:
            releases += (
                f'<a href="{url}{branch}/{data["uninstaller"]["link"]}">Uninstaller</a> | '
                f'<a href="{url}{branch}/{data["magisk"]["note"]}">Changelog</a>\n'
            )
        else:
            releases += (
                f'<a href="{data["uninstaller"]["link"]}">Uninstaller</a>\n'
                f'<a href="{data["magisk"]["note"]}">Changelog</a>\n'
            )

    await http.aclose()
    await message.reply(releases, disable_web_page_preview=True)


@register(cmds="phh")
@disableable_dec("phh")
async def phh(message):
    async with httpx.AsyncClient(http2=True) as http:
        fetch = await http.get(
            "https://api.github.com/repos/phhusson/treble_experimentations/releases/latest"
        )
        usr = json.loads(fetch.content)
    text = "<b>Phh's latest GSI release(s):</b>\n"
    for i in range(len(usr)):
        try:
            name = usr["assets"][i]["name"]
            url = usr["assets"][i]["browser_download_url"]
            text += f"<a href='{url}'>{name}</a>\n"
        except IndexError:
            continue

    await http.aclose()
    await message.reply(text)


@register(cmds="phhmagisk")
@disableable_dec("phhmagisk")
async def phh_magisk(message):
    async with httpx.AsyncClient(http2=True) as http:
        fetch = await http.get(
            "https://api.github.com/repos/expressluke/phh-magisk-builder/releases/latest"
        )
        usr = json.loads(fetch.content)
    text = "<b>Phh's latest Magisk release(s):</b>\n"
    for i in range(len(usr)):
        try:
            usr["assets"][i]["name"]
            url = usr["assets"][i]["browser_download_url"]
            tag = usr["tag_name"]
            size_bytes = usr["assets"][i]["size"]
            size = float("{:.2f}".format((size_bytes / 1024) / 1024))
            text += f"<b>Tag:</b> <code>{tag}</code>\n"
            text += f"<b>Size</b>: <code>{size} MB</code>\n\n"
            btn = "Click here to download!"
            button = InlineKeyboardMarkup().add(InlineKeyboardButton(text=btn, url=url))
        except IndexError:
            continue

    await http.aclose()
    await message.reply(text, reply_markup=button)
    return


@register(cmds="twrp")
@disableable_dec("twrp")
async def twrp(message):
    device = get_arg(message).lower()

    if not device:
        m = "Type the device codename, example: <code>/twrp j7xelte</code>"
        await message.reply(m)
        return

    async with httpx.AsyncClient(http2=True) as http:
        url = await http.get(f"https://eu.dl.twrp.me/{device}/")
    if url.status_code == 404:
        m = f"TWRP is not available for <code>{device}</code>"
        await message.reply(m)
        return

    else:
        m = "<b><u>TeamWin Recovery <i>official</i> release</u></b>\n"
        m += f"  <b>Device:</b> {device}\n"
        page = BeautifulSoup(url.content, "lxml")
        date = page.find("em").text.strip()
        m += f"  <b>Updated:</b> <code>{date}</code>\n"
        trs = page.find("table").find_all("tr")
        row = 2 if trs[0].find("a").text.endswith("tar") else 1

        for i in range(row):
            download = trs[i].find("a")
            dl_link = f"https://dl.twrp.me{download['href']}"
            dl_file = download.text
            size = trs[i].find("span", {"class": "filesize"}).text
        m += f"  <b>Size:</b> <code>{size}</code>\n"
        m += f"  <b>File:</b> <code>{dl_file.lower()}</code>"
        btn = "⬇️ Download"
        button = InlineKeyboardMarkup().add(InlineKeyboardButton(text=btn, url=dl_link))

        await http.aclose()
        await message.reply(m, reply_markup=button)


@decorator.register(cmds=["samcheck", "samget"])
@disableable_dec("samcheck")
async def check(message):
    try:
        msg_args = message.text.split()
        temp = msg_args[1]
        csc = msg_args[2]
    except IndexError:
        m = f"Please type your device <b>MODEL</b> and <b>CSC</b> into it!\ni.e <code>/{get_cmd(message)} SM-J710MN ZTO</code>!"
        await message.reply(m)
        return

    model = "sm-" + temp if not temp.upper().startswith("SM-") else temp
    async with httpx.AsyncClient(http2=True) as http:
        fota = await http.get(
            f"http://fota-cloud-dn.ospserver.net/firmware/{csc.upper()}/{model.upper()}/version.xml"
        )
        test = await http.get(
            f"http://fota-cloud-dn.ospserver.net/firmware/{csc.upper()}/{model.upper()}/version.test.xml"
        )
    await http.aclose()
    if test.status_code != 200:
        m = f"Couldn't find any firmwares for {temp.upper()} - {csc.upper()}, please refine your search or try again later!"
        await message.reply(m)
        return

    page1 = BeautifulSoup(fota.content, "lxml")
    page2 = BeautifulSoup(test.content, "lxml")
    os1 = page1.find("latest").get("o")
    os2 = page2.find("latest").get("o")
    if page1.find("latest").text.strip():
        pda1, csc1, phone1 = page1.find("latest").text.strip().split("/")
        m = f"<b>MODEL:</b> <code>{model.upper()}</code>\n<b>CSC:</b> <code>{csc.upper()}</code>\n\n"
        m += "<b>Latest available firmware:</b>\n"
        m += f"• PDA: <code>{pda1}</code>\n• CSC: <code>{csc1}</code>\n"
        if phone1:
            m += f"• Phone: <code>{phone1}</code>\n"
        if os1:
            m += f"• Android: <code>{os1}</code>\n"
        m += "\n"
    else:
        m = f"<b>No public release found for {model.upper()} and {csc.upper()}.</b>\n\n"
    m += "<b>Latest test firmware:</b>\n"
    if len(page2.find("latest").text.strip().split("/")) == 3:
        pda2, csc2, phone2 = page2.find("latest").text.strip().split("/")
        m += f"• PDA: <code>{pda2}</code>\n• CSC: <code>{csc2}</code>\n"
        if phone2:
            m += f"• Phone: <code>{phone2}</code>\n"
        if os2:
            m += f"• Android: <code>{os2}</code>\n"
    else:
        md5 = page2.find("latest").text.strip()
        m += f"• Hash: <code>{md5}</code>\n• Android: <code>{os2}</code>\n"

    if get_cmd(message) == "samcheck":
        await message.reply(m)

    elif get_cmd(message) == "samget":
        m += "\n<b>Download from below:</b>\n"
        buttons = InlineKeyboardMarkup()
        buttons.add(
            InlineKeyboardButton(
                "SamMobile",
                url="https://www.sammobile.com/samsung/firmware/{}/{}/".format(
                    model.upper(), csc.upper()
                ),
            ),
            InlineKeyboardButton(
                "SamFw",
                url="https://samfw.com/firmware/{}/{}/".format(
                    model.upper(), csc.upper()
                ),
            ),
            InlineKeyboardButton(
                "SamFrew",
                url="https://samfrew.com/model/{}/region/{}/".format(
                    model.upper(), csc.upper()
                ),
            ),
        )

        await message.reply(m, reply_markup=buttons)


@decorator.register(cmds=["ofox", "of"])
@disableable_dec("ofox")
async def orangefox(message):
    API_HOST = "https://api.orangefox.download/v3/"
    try:
        args = message.text.split()
        codename = args[1].lower()
    except BaseException:
        codename = ""
    try:
        build_type = args[2].lower()
    except BaseException:
        build_type = ""

    if build_type == "":
        build_type = "stable"

    if codename == "devices" or codename == "":
        reply_text = (
            f"<b>OrangeFox Recovery <i>{build_type}</i> is currently avaible for:</b>"
        )

        async with httpx.AsyncClient(http2=True) as http:
            data = await http.get(
                API_HOST + f"devices/?release_type={build_type}&sort=device_name_asc"
            )
            devices = json.loads(data.text)
            await http.aclose()
        try:
            for device in devices["data"]:
                reply_text += (
                    f"\n - {device['full_name']} (<code>{device['codename']}</code>)"
                )
        except BaseException:
            await message.reply(
                f"'<b>{build_type}</b>' is not a type of build available, the types are just '<b>beta</b>' or '<b>stable</b>'."
            )
            return

        if build_type == "stable":
            reply_text += (
                "\n\n"
                + f"To get the latest Stable release use <code>/ofox (codename)</code>, for example: <code>/ofox raphael</code>"
            )
        elif build_type == "beta":
            reply_text += (
                "\n\n"
                + f"To get the latest Beta release use <code>/ofox (codename) beta</code>, for example: <code>/ofox raphael beta</code>"
            )
        await message.reply(reply_text)
        return

    async with httpx.AsyncClient(http2=True) as http:
        data = await http.get(API_HOST + f"devices/get?codename={codename}")
        device = json.loads(data.text)
        await http.aclose()
    if data.status_code == 404:
        await message.reply("Device is not found!")
        return

    async with httpx.AsyncClient(http2=True) as http:
        data = await http.get(
            API_HOST
            + f"releases/?codename={codename}&type={build_type}&sort=date_desc&limit=1"
        )
        if data.status_code == 404:
            btn = "Device's page"
            url = f"https://orangefox.download/device/{device['codename']}"
            button = InlineKeyboardMarkup().add(InlineKeyboardButton(text=btn, url=url))
            await message.reply(
                f"⚠️ There is no '<b>{build_type}</b>' releases for <b>{device['full_name']}</b>.",
                reply_markup=button,
                disable_web_page_preview=True,
            )
            return
        find_id = json.loads(data.text)
        await http.aclose()
        for build in find_id["data"]:
            file_id = build["_id"]

    async with httpx.AsyncClient(http2=True) as http:
        data = await http.get(API_HOST + f"releases/get?_id={file_id}")
        release = json.loads(data.text)
        await http.aclose()
    if data.status_code == 404:
        await message.reply("Release is not found!")
        return

    reply_text = f"<u><b>OrangeFox Recovery <i>{build_type}</i> release</b></u>\n"
    reply_text += ("  <b>Device:</b> {fullname} (<code>{codename}</code>)\n").format(
        fullname=device["full_name"], codename=device["codename"]
    )
    reply_text += ("  <b>Version:</b> {}\n").format(release["version"])
    reply_text += ("  <b>Release date:</b> {}\n").format(
        time.strftime("%d/%m/%Y", time.localtime(release["date"]))
    )

    reply_text += ("  <b>Maintainer:</b> {name}\n").format(
        name=device["maintainer"]["name"]
    )
    changelog = release["changelog"]
    try:
        reply_text += "  <u><b>Changelog:</b></u>\n"
        for entry_num in range(len(changelog)):
            if entry_num == 10:
                break
            reply_text += f"    - {changelog[entry_num]}\n"
    except BaseException:
        pass

    btn = "⬇️ Download"
    url = release["mirrors"]["DL"]
    button = InlineKeyboardMarkup().add(InlineKeyboardButton(text=btn, url=url))
    await message.reply(reply_text, reply_markup=button, disable_web_page_preview=True)
    return


__mod_name__ = "Android"

__help__ = """
Module specially made for Android users.

<b>GSI</b>
- /phh: Get the latest PHH AOSP GSIs.
- /phhmagisk: Get the latest PHH Magisk.

<b>Device firmware:</b>
- /samcheck (model) (csc): Samsung only - shows the latest firmware info for the given device, taken from samsung servers.
- /samget (model) (csc): Similar to the <code>/samcheck</code> command but having download buttons.

<b>Misc</b>
- /magisk: Get latest Magisk releases.
- /twrp (codename): Gets latest TWRP for the android device using the codename.
- /ofox (codename): Gets latest OFRP for the android device using the codename.
- /ofox devices: Sends the list of devices with stable releases supported by OFRP.
- /models (codename): Search for Android device models using codename.
- /whatis (codename): Find out which smartphone is using the codename.
"""
