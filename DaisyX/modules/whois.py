from datetime import datetime

from pyrogram import filters
from pyrogram.errors import PeerIdInvalid
from pyrogram.types import Message, User

from DaisyX.services.pyrogram import pbot
import aiohttp
from asyncio import sleep
from DaisyX.services.pyrogram import pbot as kp


def ReplyCheck(message: Message):
    reply_id = None

    if message.reply_to_message:
        reply_id = message.reply_to_message.message_id

    elif not message.from_user.is_self:
        reply_id = message.message_id

    return reply_id


infotext = (
    "**[{full_name}](tg://user?id={user_id})**\n"
    " * UserID: `{user_id}`\n"
    " * First Name: `{first_name}`\n"
    " * Last Name: `{last_name}`\n"
    " * Username: `{username}`\n"
    " * Last Online: `{last_online}`\n"
    " * Bio: {bio}"
)


def LastOnline(user: User):
    if user.is_bot:
        return ""
    elif user.status == "recently":
        return "Recently"
    elif user.status == "within_week":
        return "Within the last week"
    elif user.status == "within_month":
        return "Within the last month"
    elif user.status == "long_time_ago":
        return "A long time ago :("
    elif user.status == "online":
        return "Currently Online"
    elif user.status == "offline":
        return datetime.fromtimestamp(user.status.date).strftime(
            "%a, %d %b %Y, %H:%M:%S"
        )


def FullName(user: User):
    return user.first_name + " " + user.last_name if user.last_name else user.first_name


@pbot.on_message(filters.command("whois"))
async def whois(client, message):
    cmd = message.command
    if not message.reply_to_message and len(cmd) == 1:
        get_user = message.from_user.id
    elif len(cmd) == 1:
        get_user = message.reply_to_message.from_user.id
    elif len(cmd) > 1:
        get_user = cmd[1]
        try:
            get_user = int(cmd[1])
        except ValueError:
            pass
    try:
        user = await client.get_users(get_user)
    except PeerIdInvalid:
        await message.reply("I don't know that User.")
        return
    desc = await client.get_chat(get_user)
    desc = desc.description
    await message.reply_text(
        infotext.format(
            full_name=FullName(user),
            user_id=user.id,
            user_dc=user.dc_id,
            first_name=user.first_name,
            last_name=user.last_name if user.last_name else "",
            username=user.username if user.username else "",
            last_online=LastOnline(user),
            bio=desc if desc else "`No bio set up.`",
        ),
        disable_web_page_preview=True,
    )



class AioHttp:
    @staticmethod
    async def get_json(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.json()

    @staticmethod
    async def get_text(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.text()

    @staticmethod
    async def get_raw(link):
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as resp:
                return await resp.read()


@kp.on_message(filters.command("spwinfo"))
async def lookup(client, message):
    cmd = message.command
    if not message.reply_to_message and len(cmd) == 1:
        get_user = message.from_user.id
    elif len(cmd) == 1:
        if message.reply_to_message.forward_from:
            get_user = message.reply_to_message.forward_from.id
        else:
            get_user = message.reply_to_message.from_user.id
    elif len(cmd) > 1:
        get_user = cmd[1]
        try:
            get_user = int(cmd[1])
        except ValueError:
            pass
    try:
        user = await client.get_chat(get_user)
    except PeerIdInvalid:
        await message.reply_text("I don't know that User.")
        sleep(2)
        return
    url = f"https://api.intellivoid.net/spamprotection/v1/lookup?query={user.id}"
    a = await AioHttp().get_json(url)
    response = a["success"]
    if response is True:
        date = a["results"]["last_updated"]
        stats = f"**◢ Intellivoid• SpamProtection Info**:\n"
        stats += f' • **Updated on**: `{datetime.fromtimestamp(date).strftime("%Y-%m-%d %I:%M:%S %p")}`\n'
        stats += (
            f" • **Chat Info**: [Link](t.me/SpamProtectionBot/?start=00_{user.id})\n"
        )

        if a["results"]["attributes"]["is_potential_spammer"] is True:
            stats += f" • **User**: `USERxSPAM`\n"
        elif a["results"]["attributes"]["is_operator"] is True:
            stats += f" • **User**: `USERxOPERATOR`\n"
        elif a["results"]["attributes"]["is_agent"] is True:
            stats += f" • **User**: `USERxAGENT`\n"
        elif a["results"]["attributes"]["is_whitelisted"] is True:
            stats += f" • **User**: `USERxWHITELISTED`\n"

        stats += f' • **Type**: `{a["results"]["entity_type"]}`\n'
        stats += (
            f' • **Language**: `{a["results"]["language_prediction"]["language"]}`\n'
        )
        stats += f' • **Language Probability**: `{a["results"]["language_prediction"]["probability"]}`\n'
        stats += f"**Spam Prediction**:\n"
        stats += f' • **Ham Prediction**: `{a["results"]["spam_prediction"]["ham_prediction"]}`\n'
        stats += f' • **Spam Prediction**: `{a["results"]["spam_prediction"]["spam_prediction"]}`\n'
        stats += f'**Blacklisted**: `{a["results"]["attributes"]["is_blacklisted"]}`\n'
        if a["results"]["attributes"]["is_blacklisted"] is True:
            stats += (
                f' • **Reason**: `{a["results"]["attributes"]["blacklist_reason"]}`\n'
            )
            stats += f' • **Flag**: `{a["results"]["attributes"]["blacklist_flag"]}`\n'
        stats += f'**PTID**:\n`{a["results"]["private_telegram_id"]}`\n'
        await message.reply_text(stats, disable_web_page_preview=True)
    else:
        await message.reply_text("`Cannot reach SpamProtection API`")
        await sleep(3)
        
__mod_name__ = "User Info"
__help__ = """
<b> Spam Info</b>
- /spwinfo : Check user's spam info from intellivoid's Spamprotection service
<b> Whois </b>
- /whois : Gives user's info like pyrogram
"""
