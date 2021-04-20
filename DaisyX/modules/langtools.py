import json

import requests
from google_trans_new import google_translator
from PyDictionary import PyDictionary
from telethon import *
from telethon.tl.types import *

from DaisyX.services.events import register

API_KEY = "6ae0c3a0-afdc-4532-a810-82ded0054236"
URL = "http://services.gingersoftware.com/Ginger/correct/json/GingerTheText"


@register(pattern="^/tr ?(.*)")
async def _(event):
    input_str = event.pattern_match.group(1)
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str or "en"
    elif "|" in input_str:
        lan, text = input_str.split("|")
    else:
        await event.reply(
            "`/tr <LanguageCode>` as reply to a message or `/tr <LanguageCode> | <text>`"
        )
        return
    text = text.strip()
    lan = lan.strip()
    translator = google_translator()
    try:
        translated = translator.translate(text, lang_tgt=lan)
        after_tr_text = translated
        detect_result = translator.detect(text)
        output_str = ("**TRANSLATED Succesfully** from {} to {}\n\n" "{}").format(
            detect_result[0], lan, after_tr_text
        )
        await event.reply(output_str)
    except Exception as exc:
        await event.reply(str(exc))


@register(pattern="^/spell(?: |$)(.*)")
async def _(event):
    ctext = await event.get_reply_message()
    msg = ctext.text
    #  print (msg)
    params = dict(lang="US", clientVersion="2.0", apiKey=API_KEY, text=msg)

    res = requests.get(URL, params=params)
    changes = json.loads(res.text).get("LightGingerTheTextResult")
    curr_string = ""
    prev_end = 0

    for change in changes:
        start = change.get("From")
        end = change.get("To") + 1
        suggestions = change.get("Suggestions")
        if suggestions:
            sugg_str = suggestions[0].get("Text")
            curr_string += msg[prev_end:start] + sugg_str
            prev_end = end

    curr_string += msg[prev_end:]
    await event.reply(curr_string)


dictionary = PyDictionary()


@register(pattern="^/define")
async def _(event):
    text = event.text[len("/define ") :]
    word = f"{text}"
    let = dictionary.meaning(word)
    set = str(let)
    jet = set.replace("{", "")
    net = jet.replace("}", "")
    got = net.replace("'", "")
    await event.reply(got)


@register(pattern="^/synonyms")
async def _(event):
    text = event.text[len("/synonyms ") :]
    word = f"{text}"
    let = dictionary.synonym(word)
    set = str(let)
    jet = set.replace("{", "")
    net = jet.replace("}", "")
    got = net.replace("'", "")
    await event.reply(got)


@register(pattern="^/antonyms")
async def _(event):
    text = message.text[len("/antonyms ") :]
    word = f"{text}"
    let = dictionary.antonym(word)
    set = str(let)
    jet = set.replace("{", "")
    net = jet.replace("}", "")
    got = net.replace("'", "")
    await event.reply(got)


__help__ = """
 - /tr <i>language code</i> or /tr <i>language code</i> , <i>text</i>: Type in reply to a message or (/tr <i>language code</i> , <i>text</i>) to get it's translation in the destination language
 - /define <i>text</i>: Type the word or expression you want to search\nFor example /define lesbian
 - /spell: while replying to a message, will reply with a grammar corrected version
 - /forbesify: Correct your punctuations better use the advanged spell module
 - /synonyms <i>word</i>: Find the synonyms of a word
 - /antonyms <i>word</i>: Find the antonyms of a word
"""

__mod_name__ = "Lang-Tools"
