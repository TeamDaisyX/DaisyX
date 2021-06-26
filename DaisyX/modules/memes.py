# This file is copied from @Missjuliarobot
# Full credits to original author

import asyncio
import io
import json
import os
import random
import re
import string
import subprocess
import textwrap
import urllib.request
from random import randint, randrange, uniform

import emoji
import nltk
from cowpy import cow
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from telethon import *
from telethon.tl import functions
from telethon.tl.types import *
from zalgo_text import zalgo

from DaisyX import *
from DaisyX.services.events import register
from DaisyX.services.telethon import tbot
from DaisyX.services.telethonuserbot import ubot

nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")

WIDE_MAP = {i: i + 0xFEE0 for i in range(0x21, 0x7F)}
WIDE_MAP[0x20] = 0x3000


@register(pattern="^/owu$")
async def msg(event):

    reply_tex = await event.get_reply_message()
    reply_text = reply_tex.text
    if reply_text is None:
        await event.reply("Reply to a message to make meme.")
        return
    faces = [
        "(・`ω´・)",
        ";;w;;",
        "owo",
        "UwU",
        ">w<",
        "^w^",
        r"\(^o\) (/o^)/",
        "( ^ _ ^)∠☆",
        "(ô_ô)",
        "~:o",
        ";____;",
        "(*^*)",
        "(>_",
        "(♥_♥)",
        "*(^O^)*",
        "((+_+))",
    ]
    text = re.sub(r"[rl]", "w", reply_text)
    text = re.sub(r"[ｒｌ]", "ｗ", reply_text)
    text = re.sub(r"[RL]", "W", text)
    text = re.sub(r"[ＲＬ]", "Ｗ", text)
    text = re.sub(r"n([aeiouａｅｉｏｕ])", r"ny\1", text)
    text = re.sub(r"ｎ([ａｅｉｏｕ])", r"ｎｙ\1", text)
    text = re.sub(r"N([aeiouAEIOU])", r"Ny\1", text)
    text = re.sub(r"Ｎ([ａｅｉｏｕＡＥＩＯＵ])", r"Ｎｙ\1", text)
    text = re.sub(r"\!+", " " + random.choice(faces), text)
    text = re.sub(r"！+", " " + random.choice(faces), text)
    text = text.replace("ove", "uv")
    text = text.replace("ｏｖｅ", "ｕｖ")
    text += " " + random.choice(faces)
    await event.reply(text)


@register(pattern="^/copypasta$")
async def msg(event):

    rtex = await event.get_reply_message()
    rtext = rtex.text
    if rtext is None:
        await event.reply("Reply to a message tto make meme.")
        return
    emojis = [
        "😂",
        "😂",
        "👌",
        "✌",
        "💞",
        "👍",
        "👌",
        "💯",
        "🎶",
        "👀",
        "😂",
        "👓",
        "👏",
        "👐",
        "🍕",
        "💥",
        "🍴",
        "💦",
        "💦",
        "🍑",
        "🍆",
        "😩",
        "😏",
        "👉👌",
        "👀",
        "👅",
        "😩",
        "🚰",
    ]
    reply_text = random.choice(emojis)
    b_char = random.choice(rtext).lower()
    for c in rtext:
        if c == " ":
            reply_text += random.choice(emojis)
        elif c in emojis:
            reply_text += c
            reply_text += random.choice(emojis)
        elif c.lower() == b_char:
            reply_text += "🅱️"
        else:
            if bool(random.getrandbits(1)):
                reply_text += c.upper()
            else:
                reply_text += c.lower()
    reply_text += random.choice(emojis)
    await event.reply(reply_text)


@register(pattern="^/bmoji$")
async def msg(event):

    rtex = await event.get_reply_message()
    rtext = rtex.text
    if rtext is None:
        await event.reply("Reply to a message to make meme.")
        return
    b_char = random.choice(rtext).lower()
    reply_text = rtext.replace(b_char, "🅱️").replace(b_char.upper(), "🅱️")
    await event.reply(reply_text)


@register(pattern="^/clapmoji$")
async def msg(event):

    rtex = await event.get_reply_message()
    rtext = rtex.text
    if rtext is None:
        await event.reply("Reply to a message to make meme.")
        return
    reply_text = "👏 "
    reply_text += rtext.replace(" ", " 👏 ")
    reply_text += " 👏"
    await event.reply(reply_text)


@register(pattern="^/stretch$")
async def msg(event):

    rtex = await event.get_reply_message()
    rtext = rtex.text
    if rtext is None:
        await event.reply("Reply to a message to make meme.")
        return
    count = random.randint(3, 10)
    reply_text = re.sub(r"([aeiouAEIOUａｅｉｏｕＡＥＩＯＵ])", (r"\1" * count), rtext)
    await event.reply(reply_text)


@register(pattern="^/vapor(?: |$)(.*)")
async def msg(event):

    rtex = await event.get_reply_message()
    rtext = rtex.text
    if rtext:
        data = rtext
    else:
        data = event.pattern_match.group(1)
    if data is None:
        await event.reply("Either provide some input or reply to a message.")
        return

    reply_text = str(data).translate(WIDE_MAP)
    await event.reply(reply_text)


@register(pattern="^/zalgofy$")
async def msg(event):

    rtex = await event.get_reply_message()
    rtext = rtex.text
    if rtext is None:
        await event.reply("Reply to a message to make meme.")
        return
    reply_text = zalgo.zalgo().zalgofy(rtext)
    await event.reply(reply_text)


@register(pattern="^/forbesify$")
async def msg(event):

    rtex = await event.get_reply_message()
    rtext = rtex.text
    if rtext is None:
        await event.reply("Reply to a message to make meme.")
        return
    data = rtext

    data = data.lower()
    accidentals = ["VB", "VBD", "VBG", "VBN"]
    reply_text = data.split()
    offset = 0

    tagged = dict(nltk.pos_tag(reply_text))

    for k in range(len(reply_text)):
        i = reply_text[k + offset]
        if tagged.get(i) in accidentals:
            reply_text.insert(k + offset, "accidentally")
            offset += 1

    reply_text = string.capwords(" ".join(reply_text))
    await event.reply(reply_text)


@register(pattern="^/shout (.*)")
async def msg(event):

    rtext = event.pattern_match.group(1)

    args = rtext

    if len(args) == 0:
        await event.reply("Where is text?")
        return

    msg = "```"
    text = " ".join(args)
    result = []
    result.append(" ".join(list(text)))
    for pos, symbol in enumerate(text[1:]):
        result.append(symbol + " " + "  " * pos + symbol)
    result = list("\n".join(result))
    result[0] = text[0]
    result = "".join(result)
    msg = "```\n" + result + "```"
    await event.reply(msg)


@register(pattern="^/angrymoji$")
async def msg(event):

    rtex = await event.get_reply_message()
    rtext = rtex.text
    if rtext is None:
        await event.reply("Reply to a message to make meme.")
        return
    reply_text = "😡 "
    for i in rtext:
        if i == " ":
            reply_text += " 😡 "
        else:
            reply_text += i
    reply_text += " 😡"
    await event.reply(reply_text)


@register(pattern="^/crymoji$")
async def msg(event):

    rtex = await event.get_reply_message()
    rtext = rtex.text
    if rtext is None:
        await event.reply("Reply to a message to make meme.")
        return
    reply_text = "😭 "
    for i in rtext:
        if i == " ":
            reply_text += " 😭 "
        else:
            reply_text += i
    reply_text += " 😭"
    await event.reply(reply_text)


CARBONLANG = "en"


@register(pattern="^/carbon (.*)")
async def carbon_api(e):

    jj = "`Processing..`"
    gg = await e.reply(jj)
    CARBON = "https://carbon.now.sh/?bg=rgba(239%2C40%2C44%2C1)&t=one-light&wt=none&l=application%2Ftypescript&ds=true&dsyoff=20px&dsblur=68px&wc=true&wa=true&pv=56px&ph=56px&ln=false&fl=1&fm=Hack&fs=14px&lh=143%25&si=false&es=2x&wm=false&code={code}"
    global CARBONLANG
    code = e.pattern_match.group(1)
    await gg.edit("`Processing..\n25%`")
    os.chdir("./")
    if os.path.isfile("./carbon.png"):
        os.remove("./carbon.png")
    url = CARBON.format(code=code, lang=CARBONLANG)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.binary_location = GOOGLE_CHROME_BIN
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    prefs = {"download.default_directory": "./"}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path=CHROME_DRIVER, options=chrome_options)
    driver.get(url)
    await gg.edit("`Processing..\n50%`")
    download_path = "./"
    driver.command_executor._commands["send_command"] = (
        "POST",
        "/session/$sessionId/chromium/send_command",
    )
    params = {
        "cmd": "Page.setDownloadBehavior",
        "params": {"behavior": "allow", "downloadPath": download_path},
    }
    driver.execute("send_command", params)
    driver.find_element_by_xpath("//button[contains(text(),'Export')]").click()
    await gg.edit("`Processing..\n75%`")
    while not os.path.isfile("./carbon.png"):
        await asyncio.sleep(1)
    await gg.edit("`Processing..\n100%`")
    file = "./carbon.png"
    await e.edit("`Uploading..`")
    await tbot.send_file(
        e.chat_id,
        file,
        caption="Made using [Carbon](https://carbon.now.sh/about/),\
        \na project by [Dawn Labs](https://dawnlabs.io/)",
        force_document=True,
    )
    os.remove("./carbon.png")
    driver.quit()


@register(pattern="^/deepfry(?: |$)(.*)")
async def deepfryer(event):

    try:
        frycount = int(event.pattern_match.group(1))
        if frycount < 1:
            raise ValueError
    except ValueError:
        frycount = 1
    if event.is_reply:
        reply_message = await event.get_reply_message()
        data = await check_media(reply_message)
        if isinstance(data, bool):
            await event.reply("`I can't deep fry that!`")
            return
    else:
        await event.reply("`Reply to an image or sticker to deep fry it!`")
        return

    image = io.BytesIO()
    await tbot.download_media(data, image)
    image = Image.open(image)

    for _ in range(frycount):
        image = await deepfry(image)
    fried_io = io.BytesIO()
    fried_io.name = "image.jpeg"
    image.save(fried_io, "JPEG")
    fried_io.seek(0)
    await event.reply(file=fried_io)


async def deepfry(img: Image) -> Image:
    colours = (
        (randint(50, 200), randint(40, 170), randint(40, 190)),
        (randint(190, 255), randint(170, 240), randint(180, 250)),
    )
    img = img.copy().convert("RGB")
    img = img.convert("RGB")
    width, height = img.width, img.height
    img = img.resize(
        (int(width ** uniform(0.8, 0.9)), int(height ** uniform(0.8, 0.9))),
        resample=Image.LANCZOS,
    )
    img = img.resize(
        (int(width ** uniform(0.85, 0.95)), int(height ** uniform(0.85, 0.95))),
        resample=Image.BILINEAR,
    )
    img = img.resize(
        (int(width ** uniform(0.89, 0.98)), int(height ** uniform(0.89, 0.98))),
        resample=Image.BICUBIC,
    )
    img = img.resize((width, height), resample=Image.BICUBIC)
    img = ImageOps.posterize(img, randint(3, 7))
    overlay = img.split()[0]
    overlay = ImageEnhance.Contrast(overlay).enhance(uniform(1.0, 2.0))
    overlay = ImageEnhance.Brightness(overlay).enhance(uniform(1.0, 2.0))
    overlay = ImageOps.colorize(overlay, colours[0], colours[1])
    img = Image.blend(img, overlay, uniform(0.1, 0.4))
    img = ImageEnhance.Sharpness(img).enhance(randint(5, 300))
    return img


async def check_media(reply_message):
    if reply_message and reply_message.media:
        if reply_message.photo:
            data = reply_message.photo
        elif reply_message.document:
            if (
                DocumentAttributeFilename(file_name="AnimatedSticker.tgs")
                in reply_message.media.document.attributes
            ):
                return False
            if (
                reply_message.gif
                or reply_message.video
                or reply_message.audio
                or reply_message.voice
            ):
                return False
            data = reply_message.media.document
        else:
            return False
    else:
        return False
    if not data or data is None:
        return False
    return data


@register(pattern="^/type (.*)")
async def typewriter(typew):

    message = typew.pattern_match.group(1)
    if message:
        pass
    else:
        await typew.reply("`Give a text to type!`")
        return
    typing_symbol = "|"
    old_text = ""
    now = await typew.reply(typing_symbol)
    await asyncio.sleep(2)
    for character in message:
        old_text = old_text + "" + character
        typing_text = old_text + "" + typing_symbol
        await now.edit(typing_text)
        await asyncio.sleep(2)
        await now.edit(old_text)
        await asyncio.sleep(2)


@register(pattern="^/sticklet (.*)")
async def sticklet(event):

    R = random.randint(0, 256)
    G = random.randint(0, 256)
    B = random.randint(0, 256)

    # get the input text
    # the text on which we would like to do the magic on
    sticktext = event.pattern_match.group(1)

    # delete the userbot command,
    # i don't know why this is required
    # await event.delete()

    # https://docs.python.org/3/library/textwrap.html#textwrap.wrap
    sticktext = textwrap.wrap(sticktext, width=10)
    # converts back the list to a string
    sticktext = "\n".join(sticktext)

    image = Image.new("RGBA", (512, 512), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    fontsize = 230

    FONT_FILE = await get_font_file(ubot, "@IndianBot_Fonts")

    font = ImageFont.truetype(FONT_FILE, size=fontsize)

    while draw.multiline_textsize(sticktext, font=font) > (512, 512):
        fontsize -= 3
        font = ImageFont.truetype(FONT_FILE, size=fontsize)

    width, height = draw.multiline_textsize(sticktext, font=font)
    draw.multiline_text(
        ((512 - width) / 2, (512 - height) / 2), sticktext, font=font, fill=(R, G, B)
    )

    image_stream = io.BytesIO()
    image_stream.name = "@Julia.webp"
    image.save(image_stream, "WebP")
    image_stream.seek(0)

    # finally, reply the sticker
    await event.reply(file=image_stream, reply_to=event.message.reply_to_msg_id)
    # replacing upper line with this to get reply tags

    # cleanup
    try:
        os.remove(FONT_FILE)
    except BaseException:
        pass


async def get_font_file(client, channel_id):
    # first get the font messages
    font_file_message_s = await client.get_messages(
        entity=channel_id,
        filter=InputMessagesFilterDocument,
        # this might cause FLOOD WAIT,
        # if used too many times
        limit=None,
    )
    # get a random font from the list of fonts
    # https://docs.python.org/3/library/random.html#random.choice
    font_file_message = random.choice(font_file_message_s)
    # download and return the file path
    return await client.download_media(font_file_message)


@register(pattern=r"^/(\w+)say (.*)")
async def univsaye(cowmsg):

    """For .cowsay module, uniborg wrapper for cow which says things."""
    if not cowmsg.text[0].isalpha() and cowmsg.text[0] not in ("#", "@"):
        arg = cowmsg.pattern_match.group(1).lower()
        text = cowmsg.pattern_match.group(2)

        if arg == "cow":
            arg = "default"
        if arg not in cow.COWACTERS:
            return
        cheese = cow.get_cow(arg)
        cheese = cheese()

        await cowmsg.reply(f"`{cheese.milk(text).replace('`', '´')}`")


@register(pattern="^/basketball$")
async def _(event):
    if event.fwd_from:
        return

    input_str = print(randrange(6))
    r = await event.reply(file=InputMediaDice("🏀"))
    if input_str:
        try:
            required_number = int(input_str)
            while not r.media.value == required_number:
                await r.delete()
                r = await event.reply(file=InputMediaDice("🏀"))
        except BaseException:
            pass


@register(pattern="^/jackpot$")
async def _(event):
    if event.fwd_from:
        return

    await event.reply(file=InputMediaDice("🎰"))


@register(pattern="^/dart$")
async def _(event):
    if event.fwd_from:
        return

    input_str = print(randrange(7))
    r = await event.reply(file=InputMediaDice("🎯"))
    if input_str:
        try:
            required_number = int(input_str)
            while not r.media.value == required_number:
                await r.delete()
                r = await event.reply(file=InputMediaDice("🎯"))
        except BaseException:
            pass


# Oringinal Source from Nicegrill: https://github.com/erenmetesar/NiceGrill/
# Ported to Lynda by: @pokurt

COLORS = [
    "#F07975",
    "#F49F69",
    "#F9C84A",
    "#8CC56E",
    "#6CC7DC",
    "#80C1FA",
    "#BCB3F9",
    "#E181AC",
]


async def process(msg, user, client, reply, replied=None):
    if not os.path.isdir("resources"):
        os.mkdir("resources", 0o755)
        urllib.request.urlretrieve(
            "https://github.com/erenmetesar/modules-repo/raw/master/Roboto-Regular.ttf",
            "resources/Roboto-Regular.ttf",
        )
        urllib.request.urlretrieve(
            "https://github.com/erenmetesar/modules-repo/raw/master/Quivira.otf",
            "resources/Quivira.otf",
        )
        urllib.request.urlretrieve(
            "https://github.com/erenmetesar/modules-repo/raw/master/Roboto-Medium.ttf",
            "resources/Roboto-Medium.ttf",
        )
        urllib.request.urlretrieve(
            "https://github.com/erenmetesar/modules-repo/raw/master/DroidSansMono.ttf",
            "resources/DroidSansMono.ttf",
        )
        urllib.request.urlretrieve(
            "https://github.com/erenmetesar/modules-repo/raw/master/Roboto-Italic.ttf",
            "resources/Roboto-Italic.ttf",
        )

    # Importıng fonts and gettings the size of text
    font = ImageFont.truetype("resources/Roboto-Medium.ttf", 43, encoding="utf-16")
    font2 = ImageFont.truetype("resources/Roboto-Regular.ttf", 33, encoding="utf-16")
    mono = ImageFont.truetype("resources/DroidSansMono.ttf", 30, encoding="utf-16")
    italic = ImageFont.truetype("resources/Roboto-Italic.ttf", 33, encoding="utf-16")
    fallback = ImageFont.truetype("resources/Quivira.otf", 43, encoding="utf-16")

    # Splitting text
    maxlength = 0
    width = 0
    text = []
    for line in msg.split("\n"):
        length = len(line)
        if length > 43:
            text += textwrap.wrap(line, 43)
            maxlength = 43
            if width < fallback.getsize(line[:43])[0]:
                if "MessageEntityCode" in str(reply.entities):
                    width = mono.getsize(line[:43])[0] + 30
                else:
                    width = fallback.getsize(line[:43])[0]
            next
        else:
            text.append(line + "\n")
            if width < fallback.getsize(line)[0]:
                if "MessageEntityCode" in str(reply.entities):
                    width = mono.getsize(line)[0] + 30
                else:
                    width = fallback.getsize(line)[0]
            if maxlength < length:
                maxlength = length

    title = ""
    try:
        details = await client(
            functions.channels.GetParticipantRequest(reply.chat_id, user.id)
        )
        if isinstance(details.participant, types.ChannelParticipantCreator):
            title = details.participant.rank if details.participant.rank else "Creator"
        elif isinstance(details.participant, types.ChannelParticipantAdmin):
            title = details.participant.rank if details.participant.rank else "Admin"
    except TypeError:
        pass
    titlewidth = font2.getsize(title)[0]

    # Get user name
    lname = "" if not user.last_name else user.last_name
    tot = user.first_name + " " + lname

    namewidth = fallback.getsize(tot)[0] + 10

    if namewidth > width:
        width = namewidth
    width += titlewidth + 30 if titlewidth > width - namewidth else -(titlewidth - 30)
    height = len(text) * 40

    # Profile Photo BG
    pfpbg = Image.new("RGBA", (125, 600), (0, 0, 0, 0))

    # Draw Template
    top, middle, bottom = await drawer(width, height)
    # Profile Photo Check and Fetch
    yes = False
    color = random.choice(COLORS)
    async for photo in client.iter_profile_photos(user, limit=1):
        yes = True
    if yes:
        pfp = await client.download_profile_photo(user)
        paste = Image.open(pfp)
        os.remove(pfp)
        paste.thumbnail((105, 105))

        # Mask
        mask_im = Image.new("L", paste.size, 0)
        draw = ImageDraw.Draw(mask_im)
        draw.ellipse((0, 0, 105, 105), fill=255)

        # Apply Mask
        pfpbg.paste(paste, (0, 0), mask_im)
    else:
        paste, color = await no_photo(user, tot)
        pfpbg.paste(paste, (0, 0))

    # Creating a big canvas to gather all the elements
    canvassize = (
        middle.width + pfpbg.width,
        top.height + middle.height + bottom.height,
    )
    canvas = Image.new("RGBA", canvassize)
    draw = ImageDraw.Draw(canvas)

    y = 80
    if replied:
        # Creating a big canvas to gather all the elements
        replname = "" if not replied.sender.last_name else replied.sender.last_name
        reptot = replied.sender.first_name + " " + replname
        font2.getsize(reptot)[0]
        if reply.sticker:
            sticker = await reply.download_media()
            stimg = Image.open(sticker)
            canvas = canvas.resize((stimg.width + pfpbg.width, stimg.height + 160))
            top = Image.new("RGBA", (200 + stimg.width, 300), (29, 29, 29, 255))
            draw = ImageDraw.Draw(top)
            await replied_user(draw, reptot, replied.message.replace("\n", " "), 20)
            top = top.crop((135, 70, top.width, 300))
            canvas.paste(pfpbg, (0, 0))
            canvas.paste(top, (pfpbg.width + 10, 0))
            canvas.paste(stimg, (pfpbg.width + 10, 140))
            os.remove(sticker)
            return True, canvas
        canvas = canvas.resize((canvas.width + 60, canvas.height + 120))
        top, middle, bottom = await drawer(middle.width + 60, height + 105)
        canvas.paste(pfpbg, (0, 0))
        canvas.paste(top, (pfpbg.width, 0))
        canvas.paste(middle, (pfpbg.width, top.height))
        canvas.paste(bottom, (pfpbg.width, top.height + middle.height))
        draw = ImageDraw.Draw(canvas)
        if replied.sticker:
            replied.text = "Sticker"
        elif replied.photo:
            replied.text = "Photo"
        elif replied.audio:
            replied.text = "Audio"
        elif replied.voice:
            replied.text = "Voice Message"
        elif replied.document:
            replied.text = "Document"
        await replied_user(
            draw,
            reptot,
            replied.message.replace("\n", " "),
            maxlength + len(title),
            len(title),
        )
        y = 200
    elif reply.sticker:
        sticker = await reply.download_media()
        stimg = Image.open(sticker)
        canvas = canvas.resize((stimg.width + pfpbg.width + 30, stimg.height + 10))
        canvas.paste(pfpbg, (0, 0))
        canvas.paste(stimg, (pfpbg.width + 10, 10))
        os.remove(sticker)
        return True, canvas
    elif reply.document and not reply.audio and not reply.audio:
        docname = ".".join(reply.document.attributes[-1].file_name.split(".")[:-1])
        doctype = reply.document.attributes[-1].file_name.split(".")[-1].upper()
        if reply.document.size < 1024:
            docsize = str(reply.document.size) + " Bytes"
        elif reply.document.size < 1048576:
            docsize = str(round(reply.document.size / 1024, 2)) + " KB "
        elif reply.document.size < 1073741824:
            docsize = str(round(reply.document.size / 1024 ** 2, 2)) + " MB "
        else:
            docsize = str(round(reply.document.size / 1024 ** 3, 2)) + " GB "
        docbglen = (
            font.getsize(docsize)[0]
            if font.getsize(docsize)[0] > font.getsize(docname)[0]
            else font.getsize(docname)[0]
        )
        canvas = canvas.resize((pfpbg.width + width + docbglen, 160 + height))
        top, middle, bottom = await drawer(width + docbglen, height + 30)
        canvas.paste(pfpbg, (0, 0))
        canvas.paste(top, (pfpbg.width, 0))
        canvas.paste(middle, (pfpbg.width, top.height))
        canvas.paste(bottom, (pfpbg.width, top.height + middle.height))
        canvas = await doctype(docname, docsize, doctype, canvas)
        y = 80 if text else 0
    else:
        canvas.paste(pfpbg, (0, 0))
        canvas.paste(top, (pfpbg.width, 0))
        canvas.paste(middle, (pfpbg.width, top.height))
        canvas.paste(bottom, (pfpbg.width, top.height + middle.height))
        y = 85

    # Writing User's Name
    space = pfpbg.width + 30
    namefallback = ImageFont.truetype("resources/Quivira.otf", 43, encoding="utf-16")
    for letter in tot:
        if letter in emoji.UNICODE_EMOJI:
            newemoji, mask = await emoji_fetch(letter)
            canvas.paste(newemoji, (space, 24), mask)
            space += 40
        else:
            if not await fontTest(letter):
                draw.text((space, 20), letter, font=namefallback, fill=color)
                space += namefallback.getsize(letter)[0]
            else:
                draw.text((space, 20), letter, font=font, fill=color)
                space += font.getsize(letter)[0]

    if title:
        draw.text(
            (canvas.width - titlewidth - 20, 25), title, font=font2, fill="#898989"
        )

    # Writing all separating emojis and regular texts
    x = pfpbg.width + 30
    bold, mono, italic, link = await get_entity(reply)
    index = 0
    emojicount = 0
    textfallback = ImageFont.truetype("resources/Quivira.otf", 33, encoding="utf-16")
    textcolor = "white"
    for line in text:
        for letter in line:
            index = (
                msg.find(letter) if emojicount == 0 else msg.find(letter) + emojicount
            )
            for offset, length in bold.items():
                if index in range(offset, length):
                    font2 = ImageFont.truetype(
                        "resources/Roboto-Medium.ttf", 33, encoding="utf-16"
                    )
                    textcolor = "white"
            for offset, length in italic.items():
                if index in range(offset, length):
                    font2 = ImageFont.truetype(
                        "resources/Roboto-Italic.ttf", 33, encoding="utf-16"
                    )
                    textcolor = "white"
            for offset, length in mono.items():
                if index in range(offset, length):
                    font2 = ImageFont.truetype(
                        "resources/DroidSansMono.ttf", 30, encoding="utf-16"
                    )
                    textcolor = "white"
            for offset, length in link.items():
                if index in range(offset, length):
                    font2 = ImageFont.truetype(
                        "resources/Roboto-Regular.ttf", 30, encoding="utf-16"
                    )
                    textcolor = "#898989"
            if letter in emoji.UNICODE_EMOJI:
                newemoji, mask = await emoji_fetch(letter)
                canvas.paste(newemoji, (x, y - 2), mask)
                x += 45
                emojicount += 1
            else:
                if not await fontTest(letter):
                    draw.text((x, y), letter, font=textfallback, fill=textcolor)
                    x += textfallback.getsize(letter)[0]
                else:
                    draw.text((x, y), letter, font=font2, fill=textcolor)
                    x += font2.getsize(letter)[0]
            msg = msg.replace(letter, "¶", 1)
        y += 40
        x = pfpbg.width + 30
    return True, canvas


async def drawer(width, height):
    # Top part
    top = Image.new("RGBA", (width, 20), (0, 0, 0, 0))
    draw = ImageDraw.Draw(top)
    draw.line((10, 0, top.width - 20, 0), fill=(29, 29, 29, 255), width=50)
    draw.pieslice((0, 0, 30, 50), 180, 270, fill=(29, 29, 29, 255))
    draw.pieslice((top.width - 75, 0, top.width, 50), 270, 360, fill=(29, 29, 29, 255))

    # Middle part
    middle = Image.new("RGBA", (top.width, height + 75), (29, 29, 29, 255))

    # Bottom part
    bottom = ImageOps.flip(top)

    return top, middle, bottom


async def fontTest(letter):
    test = TTFont("resources/Roboto-Medium.ttf")
    for table in test["cmap"].tables:
        if ord(letter) in table.cmap.keys():
            return True


async def get_entity(msg):
    bold = {0: 0}
    italic = {0: 0}
    mono = {0: 0}
    link = {0: 0}
    if not msg.entities:
        return bold, mono, italic, link
    for entity in msg.entities:
        if isinstance(entity, types.MessageEntityBold):
            bold[entity.offset] = entity.offset + entity.length
        elif isinstance(entity, types.MessageEntityItalic):
            italic[entity.offset] = entity.offset + entity.length
        elif isinstance(entity, types.MessageEntityCode):
            mono[entity.offset] = entity.offset + entity.length
        elif isinstance(entity, types.MessageEntityUrl):
            link[entity.offset] = entity.offset + entity.length
        elif isinstance(entity, types.MessageEntityTextUrl):
            link[entity.offset] = entity.offset + entity.length
        elif isinstance(entity, types.MessageEntityMention):
            link[entity.offset] = entity.offset + entity.length
    return bold, mono, italic, link


async def doctype(name, size, type, canvas):
    font = ImageFont.truetype("resources/Roboto-Medium.ttf", 38)
    doc = Image.new("RGBA", (130, 130), (29, 29, 29, 255))
    draw = ImageDraw.Draw(doc)
    draw.ellipse((0, 0, 130, 130), fill="#434343")
    draw.line((66, 28, 66, 53), width=14, fill="white")
    draw.polygon([(67, 77), (90, 53), (42, 53)], fill="white")
    draw.line((40, 87, 90, 87), width=8, fill="white")
    canvas.paste(doc, (160, 23))
    draw2 = ImageDraw.Draw(canvas)
    draw2.text((320, 40), name, font=font, fill="white")
    draw2.text((320, 97), size + type, font=font, fill="#AAAAAA")
    return canvas


async def no_photo(reply, tot):
    pfp = Image.new("RGBA", (105, 105), (0, 0, 0, 0))
    pen = ImageDraw.Draw(pfp)
    color = random.choice(COLORS)
    pen.ellipse((0, 0, 105, 105), fill=color)
    letter = "" if not tot else tot[0]
    font = ImageFont.truetype("resources/Roboto-Regular.ttf", 60)
    pen.text((32, 17), letter, font=font, fill="white")
    return pfp, color


async def emoji_fetch(emoji):
    emojis = json.loads(
        urllib.request.urlopen(
            "https://github.com/erenmetesar/modules-repo/raw/master/emojis.txt"
        )
        .read()
        .decode()
    )
    if emoji in emojis:
        img = emojis[emoji]
        return await transparent(
            urllib.request.urlretrieve(img, "resources/emoji.png")[0]
        )
    img = emojis["⛔"]
    return await transparent(urllib.request.urlretrieve(img, "resources/emoji.png")[0])


async def transparent(emoji):
    emoji = Image.open(emoji).convert("RGBA")
    emoji.thumbnail((40, 40))

    # Mask
    mask = Image.new("L", (40, 40), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, 40, 40), fill=255)
    return emoji, mask


async def replied_user(draw, tot, text, maxlength, title):
    namefont = ImageFont.truetype("resources/Roboto-Medium.ttf", 38)
    namefallback = ImageFont.truetype("resources/Quivira.otf", 38)
    textfont = ImageFont.truetype("resources/Roboto-Regular.ttf", 32)
    textfallback = ImageFont.truetype("resources/Roboto-Medium.ttf", 38)
    maxlength = maxlength + 7 if maxlength < 10 else maxlength
    text = text[: maxlength - 2] + ".." if len(text) > maxlength else text
    draw.line((165, 90, 165, 170), width=5, fill="white")
    space = 0
    for letter in tot:
        if not await fontTest(letter):
            draw.text((180 + space, 86), letter, font=namefallback, fill="#888888")
            space += namefallback.getsize(letter)[0]
        else:
            draw.text((180 + space, 86), letter, font=namefont, fill="#888888")
            space += namefont.getsize(letter)[0]
    space = 0
    for letter in text:
        if not await fontTest(letter):
            draw.text((180 + space, 132), letter, font=textfallback, fill="#888888")
            space += textfallback.getsize(letter)[0]
        else:
            draw.text((180 + space, 132), letter, font=textfont, fill="white")
            space += textfont.getsize(letter)[0]


@register(pattern="^/quotly$")
async def _(event):
    if event.fwd_from:
        return

    reply = await event.get_reply_message()
    msg = reply.message
    repliedreply = await reply.get_reply_message()
    user = (
        await event.client.get_entity(reply.forward.sender)
        if reply.fwd_from
        else reply.sender
    )
    res, canvas = await process(msg, user, event.client, reply, repliedreply)
    if not res:
        return
    canvas.save("sticker.webp")
    await event.client.send_file(
        event.chat_id, "sticker.webp", reply_to=event.reply_to_msg_id
    )
    os.remove("sticker.webp")


EMOJI_PATTERN = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "]+"
)


def deEmojify(inputString: str) -> str:
    """Remove emojis and other non-safe characters from string"""
    return re.sub(EMOJI_PATTERN, "", inputString)


# Made By @MissJulia_Robot


@register(pattern="^/animate (.*)")
async def stickerizer(event):

    newtext = event.pattern_match.group(1)
    animus = [20, 32, 33, 40, 41, 42, 58]
    sticcers = await ubot.inline_query(
        "stickerizerbot", f"#{random.choice(animus)}{(deEmojify(newtext))}"
    )
    null = await sticcers[0].download_media(TEMP_DOWNLOAD_DIRECTORY)
    bara = str(null)
    await event.client.send_file(event.chat_id, bara, reply_to=event.id)
    os.remove(bara)


@register(pattern="^/dice$")
async def _(event):
    if event.fwd_from:
        return

    input_str = print(randrange(7))
    r = await event.reply(file=InputMediaDice(""))
    if input_str:
        try:
            required_number = int(input_str)
            while not r.media.value == required_number:
                await r.delete()
                r = await event.reply(file=InputMediaDice(""))
        except BaseException:
            pass


@register(pattern="^/fortune$")
async def fortunate(event):
    if event.fwd_from:
        return

    jit = subprocess.check_output(["python", "fortune.py"])
    pit = jit.decode()
    await event.reply(pit)


ABUSE_STRINGS = (
    "Fuck off",
    "Stfu go fuck yourself",
    "Ur mum gey",
    "Ur dad lesbo",
    "You Assfucker",
    "Nigga",
    "Ur granny tranny",
    "you noob",
    "Relax your Rear,ders nothing to fear,The Rape train is finally here",
    "Stfu bc",
    "Stfu and Gtfo U nub",
    "GTFO bsdk",
    "CUnt",
    "Madharchod",
    " Gay is here",
    "Ur dad gey bc ",
)

EYES = [
    ["⌐■", "■"],
    [" ͠°", " °"],
    ["⇀", "↼"],
    ["´• ", " •`"],
    ["´", "`"],
    ["`", "´"],
    ["ó", "ò"],
    ["ò", "ó"],
    ["⸌", "⸍"],
    [">", "<"],
    ["Ƹ̵̡", "Ʒ"],
    ["ᗒ", "ᗕ"],
    ["⟃", "⟄"],
    ["⪧", "⪦"],
    ["⪦", "⪧"],
    ["⪩", "⪨"],
    ["⪨", "⪩"],
    ["⪰", "⪯"],
    ["⫑", "⫒"],
    ["⨴", "⨵"],
    ["⩿", "⪀"],
    ["⩾", "⩽"],
    ["⩺", "⩹"],
    ["⩹", "⩺"],
    ["◥▶", "◀◤"],
    ["◍", "◎"],
    ["/͠-", "┐͡-\\"],
    ["⌣", "⌣”"],
    [" ͡⎚", " ͡⎚"],
    ["≋"],
    ["૦ઁ"],
    ["  ͯ"],
    ["  ͌"],
    ["ළ"],
    ["◉"],
    ["☉"],
    ["・"],
    ["▰"],
    ["ᵔ"],
    [" ﾟ"],
    ["□"],
    ["☼"],
    ["*"],
    ["`"],
    ["⚆"],
    ["⊜"],
    [">"],
    ["❍"],
    ["￣"],
    ["─"],
    ["✿"],
    ["•"],
    ["T"],
    ["^"],
    ["ⱺ"],
    ["@"],
    ["ȍ"],
    ["  "],
    ["  "],
    ["x"],
    ["-"],
    ["$"],
    ["Ȍ"],
    ["ʘ"],
    ["Ꝋ"],
    [""],
    ["⸟"],
    ["๏"],
    ["ⴲ"],
    ["◕"],
    ["◔"],
    ["✧"],
    ["■"],
    ["♥"],
    [" ͡°"],
    ["¬"],
    [" º "],
    ["⨶"],
    ["⨱"],
    ["⏓"],
    ["⏒"],
    ["⍜"],
    ["⍤"],
    ["ᚖ"],
    ["ᴗ"],
    ["ಠ"],
    ["σ"],
    ["☯"],
]

MOUTHS = [
    ["v"],
    ["ᴥ"],
    ["ᗝ"],
    ["Ѡ"],
    ["ᗜ"],
    ["Ꮂ"],
    ["ᨓ"],
    ["ᨎ"],
    ["ヮ"],
    ["╭͜ʖ╮"],
    [" ͟ل͜"],
    [" ͜ʖ"],
    [" ͟ʖ"],
    [" ʖ̯"],
    ["ω"],
    [" ³"],
    [" ε "],
    ["﹏"],
    ["□"],
    ["ل͜"],
    ["‿"],
    ["╭╮"],
    ["‿‿"],
    ["▾"],
    ["‸"],
    ["Д"],
    ["∀"],
    ["!"],
    ["人"],
    ["."],
    ["ロ"],
    ["_"],
    ["෴"],
    ["ѽ"],
    ["ഌ"],
    ["⏠"],
    ["⏏"],
    ["⍊"],
    ["⍘"],
    ["ツ"],
    ["益"],
    ["╭∩╮"],
    ["Ĺ̯"],
    ["◡"],
    [" ͜つ"],
]

EARS = [
    ["q", "p"],
    ["ʢ", "ʡ"],
    ["⸮", "?"],
    ["ʕ", "ʔ"],
    ["ᖗ", "ᖘ"],
    ["ᕦ", "ᕥ"],
    ["ᕦ(", ")ᕥ"],
    ["ᕙ(", ")ᕗ"],
    ["ᘳ", "ᘰ"],
    ["ᕮ", "ᕭ"],
    ["ᕳ", "ᕲ"],
    ["(", ")"],
    ["[", "]"],
    ["¯\\_", "_/¯"],
    ["୧", "୨"],
    ["୨", "୧"],
    ["⤜(", ")⤏"],
    ["☞", "☞"],
    ["ᑫ", "ᑷ"],
    ["ᑴ", "ᑷ"],
    ["ヽ(", ")ﾉ"],
    ["\\(", ")/"],
    ["乁(", ")ㄏ"],
    ["└[", "]┘"],
    ["(づ", ")づ"],
    ["(ง", ")ง"],
    ["⎝", "⎠"],
    ["ლ(", "ლ)"],
    ["ᕕ(", ")ᕗ"],
    ["(∩", ")⊃━☆ﾟ.*"],
]

TOSS = (
    "Heads",
    "Tails",
)


@register(pattern="^/roll$")
async def msg(event):

    await event.reply(str(random.choice(range(1, 7))))


@register(pattern="^/toss$")
async def msg(event):
    await event.reply(random.choice(TOSS))


@register(pattern="^/abuse$")
async def msg(event):

    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        replyto = reply.sender_id
    else:
        replyto = event.sender_id
    await tbot.send_message(
        event.chat_id, random.choice(ABUSE_STRINGS), reply_to=replyto
    )


@register(pattern="^/bluetext$")
async def msg(event):

    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        replyto = reply.sender_id
    else:
        replyto = event.sender_id
    await tbot.send_message(
        event.chat_id,
        "/BLUE /TEXT /MUST /CLICK /I /AM /A /STUPID /ANIMAL /THAT /IS /ATTRACTED /TO /COLORS",
        reply_to=replyto,
    )


@register(pattern="^/rlg$")
async def _(event):

    eyes = random.choice(EYES)
    mouth = random.choice(MOUTHS)
    ears = random.choice(EARS)
    repl = format(ears + eyes + mouth + eyes + ears)
    await event.reply(repl)


@register(pattern="^/decide$")
async def _(event):

    r = randint(1, 100)
    if r <= 65:
        await event.reply("Yes.")
    elif r <= 90:
        await event.reply("NoU.")
    else:
        await event.reply("Maybe.")


@register(pattern="^/table$")
async def _(event):

    r = randint(1, 100)
    if r <= 45:
        await event.reply("(╯°□°）╯彡 ┻━┻")
    elif r <= 90:
        await event.reply("Send money to buy new table to flip")
    else:
        await event.reply("Go do some work instead of flipping tables ma boy.")


SFW_STRINGS = (
    "Owww ... Such a stupid idiot.",
    "Don't drink and type.",
    "I think you should go home or better a mental asylum.",
    "Command not found. Just like your brain.",
    "Do you realize you are making a fool of yourself? Apparently not.",
    "You can type better than that.",
    "Bot rule 544 section 9 prevents me from replying to stupid humans like you.",
    "Sorry, we do not sell brains.",
    "Believe me you are not normal.",
    "I bet your brain feels as good as new, seeing that you never use it.",
    "If I wanted to kill myself I'd climb your ego and jump to your IQ.",
    "Zombies eat brains... you're safe.",
    "You didn't evolve from apes, they evolved from you.",
    "Come back and talk to me when your I.Q. exceeds your age.",
    "I'm not saying you're stupid, I'm just saying you've got bad luck when it comes to thinking.",
    "What language are you speaking? Cause it sounds like bullshit.",
    "Stupidity is not a crime so you are free to go.",
    "You are proof that evolution CAN go in reverse.",
    "I would ask you how old you are but I know you can't count that high.",
    "As an outsider, what do you think of the human race?",
    "Brains aren't everything. In your case they're nothing.",
    "Ordinarily people live and learn. You just live.",
    "I don't know what makes you so stupid, but it really works.",
    "Keep talking, someday you'll say something intelligent! (I doubt it though)",
    "Shock me, say something intelligent.",
    "Your IQ's lower than your shoe size.",
    "Alas! Your neurotransmitters are no more working.",
    "Are you crazy you fool.",
    "Everyone has the right to be stupid but you are abusing the privilege.",
    "I'm sorry I hurt your feelings when I called you stupid. I thought you already knew that.",
    "You should try tasting cyanide.",
    "Your enzymes are meant to digest rat poison.",
    "You should try sleeping forever.",
    "Pick up a gun and shoot yourself.",
    "You could make a world record by jumping from a plane without parachute.",
    "Stop talking BS and jump in front of a running bullet train.",
    "Try bathing with Hydrochloric Acid instead of water.",
    "Try this: if you hold your breath underwater for an hour, you can then hold it forever.",
    "Go Green! Stop inhaling Oxygen.",
    "God was searching for you. You should leave to meet him.",
    "give your 100%. Now, go donate blood.",
    "Try jumping from a hundred story building but you can do it only once.",
    "You should donate your brain seeing that you never used it.",
    "Volunteer for target in an firing range.",
    "Head shots are fun. Get yourself one.",
    "You should try swimming with great white sharks.",
    "You should paint yourself red and run in a bull marathon.",
    "You can stay underwater for the rest of your life without coming back up.",
    "How about you stop breathing for like 1 day? That'll be great.",
    "Try provoking a tiger while you both are in a cage.",
    "Have you tried shooting yourself as high as 100m using a canon.",
    "You should try holding TNT in your mouth and igniting it.",
    "Try playing catch and throw with RDX its fun.",
    "I heard phogine is poisonous but i guess you wont mind inhaling it for fun.",
    "Launch yourself into outer space while forgetting oxygen on Earth.",
    "You should try playing snake and ladders, with real snakes and no ladders.",
    "Dance naked on a couple of HT wires.",
    "Active Volcano is the best swimming pool for you.",
    "You should try hot bath in a volcano.",
    "Try to spend one day in a coffin and it will be yours forever.",
    "Hit Uranium with a slow moving neutron in your presence. It will be a worthwhile experience.",
    "You can be the first person to step on sun. Have a try.",
    "People like you are the reason we have middle fingers.",
    "When your mom dropped you off at the school, she got a ticket for littering.",
    "You’re so ugly that when you cry, the tears roll down the back of your head…just to avoid your face.",
    "If you’re talking behind my back then you’re in a perfect position to kiss my a**!.",
    "Stupidity is not a crime so you are free to go.",
)


@register(pattern="^/insult$")
async def _(event):

    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        replyto = reply.sender_id
    else:
        replyto = event.sender_id
    await tbot.send_message(event.chat_id, random.choice(SFW_STRINGS), reply_to=replyto)


reactionhappy = [
    "''̵͇З= ( ▀ ͜͞ʖ▀) =Ε/̵͇/’’",
    "ʕ•ᴥ•ʔ",
    "(づ｡◕‿‿◕｡)づ",
    "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ ✧ﾟ･: *ヽ(◕ヮ◕ヽ)",
    "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
    "(☞ﾟ∀ﾟ)☞",
    "| (• ◡•)| (❍ᴥ❍Ʋ)",
    "(◕‿◕✿)",
    "(ᵔᴥᵔ)",
    "(☞ﾟヮﾟ)☞ ☜(ﾟヮﾟ☜)",
    "(づ￣ ³￣)づ",
    "♪~ ᕕ(ᐛ)ᕗ",
    "♥️‿♥️",
    "༼ つ ͡° ͜ʖ ͡° ༽つ",
    "༼ つ ಥ_ಥ ༽つ",
    "ヾ(⌐■_■)ノ♪",
    "~(˘▾˘~)",
    "◉_◉",
    "(•◡•) /",
    "(~˘▾˘)~",
    "(｡◕‿‿◕｡)",
    "☜(˚▽˚)☞",
    "(•Ω•)",
    "(｡◕‿◕｡)",
    "(っ˘ڡ˘Σ)",
    "｡◕‿‿◕｡",
    "☜(⌒▽⌒)☞",
    "｡◕‿◕｡",
    "(ღ˘⌣˘ღ)",
    "(▰˘◡˘▰)",
    "^̮^",
    "^̮^",
    ">_>",
    "(^̮^)",
    "^̮^",
    "^̮^",
]
reactionangry = [
    "▄︻̷┻═━一",
    "(▀Ĺ̯▀ )",
    "(ง ͠° ͟ل͜ ͡°)ง",
    "༼ つ ◕_◕ ༽つ",
    "ಠ_ಠ",
    "''̵͇З=( ͠° ͟ʖ ͡°)=Ε/̵͇/'",
    "(ง'̀-'́)ง",
    "(ノಠ益ಠ)ノ彡┻━┻",
    "(╯°□°)╯︵ ꞰOOQƎƆⱯɟ",
    "ლ(ಠ益ಠლ)",
    "ಠ╭╮ಠ",
    "''̵͇З=(•_•)=Ε/̵͇/''",
    "(╯°□°）╯︵ ┻━┻",
    "┻━┻ ︵ヽ(Д´)ﾉ︵ ┻━┻",
    "⌐╦╦═─",
    "（╯°□°）╯︵( .O.)",
    ":')",
    "┬──┬ ノ( ゜-゜ノ)",
    "ლ(´ڡლ)",
    "(°ロ°)☝️",
    "ლ,ᔑ•ﺪ͟͠•ᔐ.ლ",
    "┬─┬ノ( º _ ºノ)",
    "┬─┬﻿ ︵ /(.□. ）",
]

reactions = [
    "( ͡° ͜ʖ ͡°)",
    "( . •́ _ʖ •̀ .)",
    "( ಠ ͜ʖ ಠ)",
    "( ͡ ͜ʖ ͡ )",
    "(ʘ ͜ʖ ʘ)",
    "ヾ(´〇`)ﾉ♪♪♪",
    "ヽ(o´∀`)ﾉ♪♬",
    "♪♬((d⌒ω⌒b))♬♪",
    "└(＾＾)┐",
    "(￣▽￣)/♫•*¨*•.¸¸♪",
    "ヾ(⌐■_■)ノ♪",
    "乁( • ω •乁)",
    "♬♫♪◖(● o ●)◗♪♫♬",
    "(っ˘ڡ˘ς)",
    "( ˘▽˘)っ♨",
    "(　・ω・)⊃-[二二]",
    "(*´ー`)旦 旦(￣ω￣*)",
    "( ￣▽￣)[] [](≧▽≦ )",
    "(*￣▽￣)旦 且(´∀`*)",
    "(ノ ˘_˘)ノ　ζ|||ζ　ζ|||ζ　ζ|||ζ",
    "(ノ°∀°)ノ⌒･*:.｡. .｡.:*･゜ﾟ･*☆",
    "(⊃｡•́‿•̀｡)⊃━✿✿✿✿✿✿",
    "(∩` ﾛ ´)⊃━炎炎炎炎炎",
    "( ・∀・)・・・--------☆",
    "( -ω-)／占~~~~~",
    "○∞∞∞∞ヽ(^ー^ )",
    "(*＾＾)/~~~~~~~~~~◎",
    "((( ￣□)_／",
    "(ﾒ￣▽￣)︻┳═一",
    "ヽ( ･∀･)ﾉ_θ彡☆Σ(ノ `Д´)ノ",
    "(*`0´)θ☆(メ°皿°)ﾉ",
    "(; -_-)――――――C<―_-)",
    "ヽ(>_<ヽ) ―⊂|=0ヘ(^‿^ )",
    "(҂` ﾛ ´)︻デ═一 ＼(º □ º l|l)/",
    "/( .□.)＼ ︵╰(°益°)╯︵ /(.□. /)",
    "(`⌒*)O-(`⌒´Q)",
    "(っ•﹏•)っ ✴==≡눈٩(`皿´҂)ง",
    "ヾ(・ω・)メ(・ω・)ノ",
    "(*^ω^)八(⌒▽⌒)八(-‿‿- )ヽ",
    "ヽ( ⌒ω⌒)人(=^‥^= )ﾉ",
    "｡*:☆(・ω・人・ω・)｡:゜☆｡",
    "(°(°ω(°ω°(☆ω☆)°ω°)ω°)°)",
    "(っ˘▽˘)(˘▽˘)˘▽˘ς)",
    "(*＾ω＾)人(＾ω＾*)",
    r"＼(▽￣ \ (￣▽￣) / ￣▽)／",
    "(￣Θ￣)",
    "＼( ˋ Θ ´ )／",
    "( ´(00)ˋ )",
    "＼(￣(oo)￣)／",
    "／(≧ x ≦)＼",
    "／(=･ x ･=)＼",
    "(=^･ω･^=)",
    "(= ; ｪ ; =)",
    "(=⌒‿‿⌒=)",
    "(＾• ω •＾)",
    "ଲ(ⓛ ω ⓛ)ଲ",
    "ଲ(ⓛ ω ⓛ)ଲ",
    "(^◔ᴥ◔^)",
    "[(－－)]..zzZ",
    "(￣o￣) zzZZzzZZ",
    "(＿ ＿*) Z z z",
    "☆ﾐ(o*･ω･)ﾉ",
    "ε=ε=ε=ε=┌(;￣▽￣)┘",
    "ε===(っ≧ω≦)っ",
    "__φ(．．)",
    "ヾ( `ー´)シφ__",
    "( ^▽^)ψ__",
    "|･ω･)",
    "|д･)",
    "┬┴┬┴┤･ω･)ﾉ",
    "|･д･)ﾉ",
    "(*￣ii￣)",
    "(＾〃＾)",
    "m(_ _)m",
    "人(_ _*)",
    "(シ. .)シ",
    "(^_~)",
    "(>ω^)",
    "(^_<)〜☆",
    "(^_<)",
    "(づ￣ ³￣)づ",
    "(⊃｡•́‿•̀｡)⊃",
    "⊂(´• ω •`⊂)",
    "(*・ω・)ﾉ",
    "(^-^*)/",
    "ヾ(*'▽'*)",
    "(^０^)ノ",
    "(*°ｰ°)ﾉ",
    "(￣ω￣)/",
    "(≧▽≦)/",
    "w(°ｏ°)w",
    "(⊙_⊙)",
    "(°ロ°) !",
    "∑(O_O;)",
    "(￢_￢)",
    "(¬_¬ )",
    "(↼_↼)",
    "(￣ω￣;)",
    "┐('～`;)┌",
    "(・_・;)",
    "(＠_＠)",
    "(•ิ_•ิ)?",
    "ヽ(ー_ー )ノ",
    "┐(￣ヘ￣)┌",
    "┐(￣～￣)┌",
    "┐( ´ д ` )┌",
    "╮(︶▽︶)╭",
    "ᕕ( ᐛ )ᕗ",
    "(ノωヽ)",
    "(″ロ゛)",
    "(/ω＼)",
    "(((＞＜)))",
    "~(>_<~)",
    "(×_×)",
    "(×﹏×)",
    "(ノ_<。)",
    "(μ_μ)",
    "o(TヘTo)",
    "( ﾟ，_ゝ｀)",
    "( ╥ω╥ )",
    "(／ˍ・、)",
    "(つω`｡)",
    "(T_T)",
    "o(〒﹏〒)o",
    "(＃`Д´)",
    "(・`ω´・)",
    "( `ε´ )",
    "(ﾒ` ﾛ ´)",
    "Σ(▼□▼メ)",
    "(҂ `з´ )",
    "٩(╬ʘ益ʘ╬)۶",
    "↑_(ΦwΦ)Ψ",
    "(ﾉಥ益ಥ)ﾉ",
    "(＃＞＜)",
    "(；￣Д￣)",
    "(￢_￢;)",
    "(＾＾＃)",
    "(￣︿￣)",
    "ヾ( ￣O￣)ツ",
    "(ᗒᗣᗕ)՞",
    "(ノ_<。)ヾ(´ ▽ ` )",
    "ヽ(￣ω￣(。。 )ゝ",
    "(ﾉ_；)ヾ(´ ∀ ` )",
    "(´-ω-`( _ _ )",
    "(⌒_⌒;)",
    "(*/_＼)",
    "( ◡‿◡ *)",
    "(//ω//)",
    "(￣▽￣*)ゞ",
    "(„ಡωಡ„)",
    "(ﾉ´ з `)ノ",
    "(♡-_-♡)",
    "(─‿‿─)♡",
    "(´ ω `♡)",
    "(ღ˘⌣˘ღ)",
    "(´• ω •`) ♡",
    "╰(*´︶`*)╯♡",
    "(≧◡≦) ♡",
    "♡ (˘▽˘>ԅ( ˘⌣˘)",
    "σ(≧ε≦σ) ♡",
    "(˘∀˘)/(μ‿μ) ❤",
    "Σ>―(〃°ω°〃)♡→",
    "(* ^ ω ^)",
    "(o^▽^o)",
    "ヽ(・∀・)ﾉ",
    "(o･ω･o)",
    "(^人^)",
    "( ´ ω ` )",
    "(´• ω •`)",
    "╰(▔∀▔)╯",
    "(✯◡✯)",
    "(⌒‿⌒)",
    "(*°▽°*)",
    "(´｡• ᵕ •｡`)",
    "ヽ(>∀<☆)ノ",
    "＼(￣▽￣)／",
    "(o˘◡˘o)",
    "(╯✧▽✧)╯",
    "( ‾́ ◡ ‾́ )",
    "(๑˘︶˘๑)",
    "(´･ᴗ･ ` )",
    "( ͡° ʖ̯ ͡°)",
    "( ఠ ͟ʖ ఠ)",
    "( ಥ ʖ̯ ಥ)",
    "(≖ ͜ʖ≖)",
    "ヘ(￣ω￣ヘ)",
    "(ﾉ≧∀≦)ﾉ",
    "└(￣-￣└))",
    "┌(＾＾)┘",
    "(^_^♪)",
    "(〜￣△￣)〜",
    "(｢• ω •)｢",
    "( ˘ ɜ˘) ♬♪♫",
    "( o˘◡˘o) ┌iii┐",
    "♨o(>_<)o♨",
    "( ・・)つ―{}@{}@{}-",
    "(*´з`)口ﾟ｡ﾟ口(・∀・ )",
    "( *^^)o∀*∀o(^^* )",
    "-●●●-ｃ(・・ )",
    "(ﾉ≧∀≦)ﾉ ‥…━━━★",
    "╰( ͡° ͜ʖ ͡° )つ──☆*:・ﾟ",
    "(∩ᄑ_ᄑ)⊃━☆ﾟ*･｡*･:≡( ε:)",
]


@register(pattern="^/react$")
async def _(event):

    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        replyto = reply.sender_id
    else:
        replyto = event.sender_id
    react = random.choice(reactions)
    await event.reply(react, reply_to=replyto)


@register(pattern="^/rhappy$")
async def _(event):

    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        replyto = reply.sender_id
    else:
        replyto = event.sender_id
    rhappy = random.choice(reactionhappy)
    await event.reply(rhappy, reply_to=replyto)


@register(pattern="^/rangry$")
async def _(event):

    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        replyto = reply.sender_id
    else:
        replyto = event.sender_id
    rangry = random.choice(reactionangry)
    await event.reply(rangry, reply_to=replyto)


file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
**Some memes command, find it all out yourself !**

 - /owo: OWO de text
 - /stretch: STRETCH de text
 - /clapmoji: Type in reply to a message and see magic
 - /bmoji: Type in reply to a message and see magic
 - /copypasta: Type in reply to a message and see magic
 - /vapor: owo vapor dis
 - /shout <i>text</i>: Write anything that u want it to should
 - /zalgofy: reply to a message to glitch it out!
 - /table: get flip/unflip :v.
 - /decide: Randomly answers yes/no/maybe
 - /bluetext: Must type for fun
 - /toss: Tosses A coin
 - /abuse: Abuses the cunt
 - /insult: Insult the cunt
 - /slap: Slaps the cunt
 - /roll: Roll a dice.
 - /rlg: Join ears,nose,mouth and create an emo ;-;
 - /react: Check on your own
 - /rhappy: Check on your own
 - /rangry: Check on your own
 - /angrymoji: Check on your own
 - /crymoji: Check on your own
 - /cowsay, /tuxsay , /milksay , /kisssay , /wwwsay , /defaultsay , /bunnysay , /moosesay , /sheepsay , /rensay , /cheesesay , /ghostbusterssay , /skeletonsay <i>text</i>: Returns a stylish art text from the given text
 - /deepfry: Type this in reply to an image/sticker to roast the image/sticker
 - /figlet: Another Style art
 - /dice: Roll A dice
 - /dart: Throw a dart and try your luck
 - /basketball: Try your luck if you can enter the ball in the ring
 - /type <i>text</i>: Make the bot type something for you in a professional way
 - /carbon <i>text</i>: Beautifies your text and enwraps inside a terminal image [ENGLISH ONLY]
 - /sticklet <i>text</i>: Turn a text into a sticker
 - /fortune: gets a random fortune quote
 - /quotly: Type /quotly in reply to a message to make a sticker of that
 - /animate: Enwrap your text in a beautiful anime
 
"""

__mod_name__ = "Memes"
