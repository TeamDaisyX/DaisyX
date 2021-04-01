import os
import re
from time import time

import emoji
from coffeehouse.api import API
from coffeehouse.exception import CoffeeHouseError as CFError
from coffeehouse.lydia import LydiaAI
from google_trans_new import google_translator
from gtts import gTTS, gTTSError
from telethon import events, types
from telethon.tl import functions

import DaisyX.services.sql.chatbot_sql as sql
from DaisyX import BOT_ID
from DaisyX.config import get_str_key
from DaisyX.services.events import register
from DaisyX.services.telethon import tbot

# from DaisyX.services.sql.talk_mode_sql import add_talkmode, rmtalkmode, get_all_chat_id, is_talkmode_indb
translator = google_translator()


def extract_emojis(s):
    return "".join(c for c in s if c in emoji.UNICODE_EMOJI)


LYDIA_API_KEY = get_str_key("LYDIA_API_KEY", required=False)
CoffeeHouseAPI = API(LYDIA_API_KEY)
api_client = LydiaAI(CoffeeHouseAPI)
en_chats = []
ws_chats = []


async def can_change_info(message):
    try:
        result = await tbot(
            functions.channels.GetParticipantRequest(
                channel=message.chat_id,
                user_id=message.sender_id,
            )
        )
        p = result.participant
        return isinstance(p, types.ChannelParticipantCreator) or (
            isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.change_info
        )
    except Exception:
        return False


"""    
@tbot.on(events.NewMessage(pattern="/talkmode (.*)"))
async def close_ws(event):
    
    if not event.is_group:
        await event.reply("You Can Only do this in Groups.")
        return
    input_str = event.pattern_match.group(1)
    if not await is_admin(event, BOT_ID): 
        await event.reply("`I Should Be Admin To Do This!`")
        return
    if await is_admin(event, event.message.sender_id):      
        if (input_str == 'on' or input_str == 'On' or input_str == 'ON' or input_str == 'enable'):
          if event.chat_id in ws_chats:  
              await event.reply("This Chat is Has Already enabled talk mode.")
              return
          ws_chats.append(event.chat_id)
          await event.reply(f"**Added Chat {event.chat.title} With Id {event.chat_id} To Database. I'll talk in here**")
        elif (input_str == 'off' or input_str == 'Off' or input_str == 'OFF' or input_str == 'disable'):

          if event.chat_id in ws_chats:
              await event.reply("This Chat is Has Not Enabled Night Mode.")
              return
          ws_chats.remove(event.chat_id)
          await event.reply(f"**Removed Chat {event.chat.title} With Id {event.chat_id} From Database. You can't hear my voice anymore**")
        else:
            await event.reply(
                "I undestand `/talkmode on` and `/talkmode off` only"
            )
    else:
        await event.reply("`You Should Be Admin To Do This!`")
        return   
    
"""


@register(pattern="^/enlydia$")
async def _(event):
    if event.is_group:
        if not await can_change_info(message=event):
            return
    else:
        return
    global api_client
    chat = event.chat

    send = await event.get_sender()
    await tbot.get_entity(send)
    is_chat = sql.is_chat(chat.id)
    if not is_chat:
        ses = api_client.create_session()
        ses_id = str(ses.id)
        expires = str(ses.expires)
        sql.set_ses(chat.id, ses_id, expires)
        if not event.chat_id in en_chats:
            en_chats.append(event.chat_id)
        await event.reply("English AI successfully enabled for this chat!")
        return
    if not event.chat_id in en_chats:
        en_chats.append(event.chat_id)
        await event.reply("English only AI activated!")
    await event.reply("AI is already enabled for this chat!")
    return ""


@register(pattern="^/addlydia$")
async def _(event):
    if event.is_group:
        if not await can_change_info(message=event):
            return
    else:
        return
    global api_client
    chat = event.chat
    send = await event.get_sender()
    await tbot.get_entity(send)
    is_chat = sql.is_chat(chat.id)
    if not is_chat:
        ses = api_client.create_session()
        ses_id = str(ses.id)
        expires = str(ses.expires)
        sql.set_ses(chat.id, ses_id, expires)
        if event.chat_id in en_chats:
            en_chats.remove(event.chat_id)
        await event.reply("AI successfully enabled for this chat!")
        return
    await event.reply("AI is already enabled for this chat!")
    return ""


@register(pattern="^/rmlydia$")
async def _(event):
    if event.is_group:
        if not await can_change_info(message=event):
            return
    else:
        return
    chat = event.chat
    send = await event.get_sender()
    await tbot.get_entity(send)
    is_chat = sql.is_chat(chat.id)
    if not is_chat:
        await event.reply("AI isn't enabled here in the first place!")
        return ""
    if event.chat_id in en_chats:
        en_chats.remove(event.chat_id)
    sql.rem_chat(chat.id)
    await event.reply("AI disabled successfully!")


@tbot.on(events.NewMessage(pattern=None))
async def check_message(event):
    if event.is_group:
        pass
    else:
        return
    message = str(event.text)
    reply_msg = await event.get_reply_message()
    if message.lower() == "daizy":
        return True
    if reply_msg:
        if reply_msg.sender_id == BOT_ID:
            return True
    else:
        return False


@tbot.on(events.NewMessage(pattern=None))
async def _(event):
    if event.is_group:
        pass
    else:
        return
    global api_client
    msg = str(event.text)
    chat = event.chat
    is_chat = sql.is_chat(chat.id)
    if not is_chat:
        return
    if msg.startswith("/") or msg.startswith("@"):
        return
    if msg:
        if not await check_message(event):
            return
        if event.chat_id in en_chats:
            sesh, exp = sql.get_ses(chat.id)
            query = msg
            try:
                if int(exp) < time():
                    ses = api_client.create_session()
                    ses_id = str(ses.id)
                    expires = str(ses.expires)
                    sql.set_ses(chat.id, ses_id, expires)
                    sesh, exp = sql.get_ses(chat.id)
            except ValueError:
                pass
            try:
                rep = api_client.think_thought(sesh, query)
                await event.reply(rep)
            except CFError as e:
                print(e)
        else:
            u = msg.split()
            emj = extract_emojis(msg)
            msg = msg.replace(emj, "")
            if (
                [(k) for k in u if k.startswith("@")]
                and [(k) for k in u if k.startswith("#")]
                and [(k) for k in u if k.startswith("/")]
                and re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []
            ):

                h = " ".join(filter(lambda x: x[0] != "@", u))
                km = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", h)
                tm = km.split()
                jm = " ".join(filter(lambda x: x[0] != "#", tm))
                hm = jm.split()
                rm = " ".join(filter(lambda x: x[0] != "/", hm))
            elif [(k) for k in u if k.startswith("@")]:

                rm = " ".join(filter(lambda x: x[0] != "@", u))
            elif [(k) for k in u if k.startswith("#")]:
                rm = " ".join(filter(lambda x: x[0] != "#", u))
            elif [(k) for k in u if k.startswith("/")]:
                rm = " ".join(filter(lambda x: x[0] != "/", u))
            elif re.findall(r"\[([^]]+)]\(\s*([^)]+)\s*\)", msg) != []:
                rm = re.sub(r"\[([^]]+)]\(\s*([^)]+)\s*\)", r"", msg)
            else:
                rm = msg
                # print (rm)
                lan = translator.detect(rm)
            msg = rm
            test = msg
            if not "en" in lan and not lan == "":
                msg = translator.translate(test, lang_tgt="en")
            sesh, exp = sql.get_ses(chat.id)
            query = msg
            try:
                if int(exp) < time():
                    ses = api_client.create_session()
                    ses_id = str(ses.id)
                    expires = str(ses.expires)
                    sql.set_ses(chat.id, ses_id, expires)
                    sesh, exp = sql.get_ses(chat.id)
            except ValueError:
                pass
            try:
                rep = api_client.think_thought(sesh, query)
                pro = rep
                if not "en" in lan and not lan == "":
                    pro = translator.translate(rep, lang_tgt=lan[0])
                if event.chat_id in ws_chats:
                    answer = pro
                    try:
                        tts = gTTS(answer, tld="com", lang=lan[0])
                        tts.save("results.mp3")
                    except AssertionError:
                        return
                    except ValueError:
                        return
                    except RuntimeError:
                        return
                    except gTTSError:
                        return
                    with open("results.mp3", "r"):
                        await tbot.send_file(
                            event.chat_id,
                            "results.mp3",
                            voice_note=True,
                            reply_to=event.id,
                        )
                    os.remove("results.mp3")
                else:
                    await event.reply(pro)
            except CFError as e:
                print(e)


__help__ = """
<b> Chatbot </b>
<i> PRESENTING DAISY AI 3.0. THE ONLY AI SYSTEM WHICH CAN DETECT & REPLY UPTO 200 LANGUAGES </i>
 - /chatbot <i>ON/OFF</i>: Enables and disables AI Chat mode (EXCLUSIVE)
* DaisyAI can detect and reply upto 200 languages by now *
 - /chatbot EN : Enables English only chatbot
 
<b> Lydia </b>
<i> PRESENTING DAISY'S LYDIA, EXCLUSIVE CHAT FEATURE DETECT UPTO 200 LANGUAGES & REPLY USING LYDIA AI</i>
 - /addlydia: Activates lydia on your group
* Daisy AI can detect and reply upto 200 languages by now *
 - /enlydia : Enables English only chat AI
 - /rmlydia : Deactivates lydia on your group (UNSTABLE)
 
<b> Assistant </b>
 - /ask <i>question</i>: Ask question from daisy
 - /ask <i> reply to voice note</i>: Get voice reply
 
<i> Lydia AI can be unstable sometimes </i>
"""

__mod_name__ = "AI Assistant"
