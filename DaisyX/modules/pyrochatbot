#    Copyright (C) 2020-2021 by @InukaAsith
#    This programme is a part of DaisyX (TG bot) project
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

#    Kang with the credits



import re
import emoji
import os
from DaisyX.services.telethon import tbot
from time import time
import asyncio, os
import DaisyX.services.sql.chatbot_sql as sql
from coffeehouse.api import API
from coffeehouse.exception import CoffeeHouseError as CFError
from coffeehouse.lydia import LydiaAI
from DaisyX import OWNER_ID, BOT_ID
from telethon import types
from telethon.tl import functions
from DaisyX.services.events import register
from telethon import events
from DaisyX.config import get_str_key
from google_trans_new import google_translator
from gtts import gTTS, gTTSError
#from DaisyX.services.sql.talk_mode_sql import add_talkmode, rmtalkmode, get_all_chat_id, is_talkmode_indb
translator = google_translator()
from DaisyX.function.telethonbasics import is_admin
from DaisyX import OWNER_ID, BOT_ID
from DaisyX.services.pyrogram import pbot
from pyrogram import filters
import asyncio, os

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

from DaisyX.services.mongo import mongodb as db_x

lydia = db_x["LYDIA"]

def add_chat(chat_id, session_id):
    stark = lydia.find_one({"chat_id": chat_id})
    if stark:
        return False
    else:
        lydia.insert_one({"chat_id": chat_id, "session_id": session_id})
        return True


def remove_chat(chat_id):
    stark = lydia.find_one({"chat_id": chat_id})
    if not stark:
        return False
    else:
        lydia.delete_one({"chat_id": chat_id})
        return True

def get_all_chats():
    r = list(lydia.find())
    if r:
        return r
    else:
        return False


def get_session(chat_id):
    stark = lydia.find_one({"chat_id": chat_id})
    if not stark:
        return False
    else:
        return stark

def update_session(chat_id, session_id):
    lydia.update_one({"chat_id": chat_id}, {"$set": {"session_id": session_id}})
    
    
    
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
    user = await tbot.get_entity(send)
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


@pbot.on_message(filters.command("addlydia") & ~filters.edited & ~filters.bot)
async def _(client,message):
    if message.chat.id in en_chats:
        en_chats.remove(message.chat.id)
    pablo = await message.reply("`Processing...`")
    session = api_client.create_session()
    session_id = session.id
    lol = add_chat(int(message.chat.id), session_id)
    if not lol:
        await pablo.edit("Lydia Already Activated In This Chat")
        return
    await pablo.edit(f"Lydia AI Successfully Added For Users In The Chat {message.chat.id}")



@pbot.on_message(filters.command("rmlydia") & ~filters.edited & ~filters.bot)
async def _(client,message):
    if message.chat.id in en_chats:
        en_chats.remove(message.chat.id)
    pablo = await message.reply("`Processing...`")
    Escobar = remove_chat(int(message.chat.id))
    if not Escobar:
        await pablo.edit("Lydia Was Not Activated In This Chat")
        return
    await pablo.edit(f"Lydia AI Successfully Deactivated For Users In The Chat {message.chat.id}")


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


@pbot.on_message(filters.text & filters.reply & ~filters.bot &
        ~filters.via_bot & ~filters.forwarded & ~filters.private ,group=2)
async def _(client,message):
    if message.reply_to_message.from_user.id != BOT_ID:
        message.continue_propagation()
    if not message.text:
        message.continue_propagation()
    msg = message.text
    print("lv1")
    if msg.startswith("/") or msg.startswith("@"):
        message.continue_propagation()
    print("hmm")
    if not get_session(int(message.chat.id)):
        message.continue_propagation()
    print("LV2",msg)
    await client.send_chat_action(message.chat.id, "typing")
    session = get_session(int(message.chat.id))

    if msg:   
       # if not await check_message(event):
            #return
        if message.chat.id in en_chats:
            try:
                session_id = session.get("session_id")
                text_rep = api_client.think_thought(session_id, msg)
            except:
                 session = api_client.create_session()
                 session_id = session.id
                 text_rep = api_client.think_thought(session_id, msg)
                 update_session(message.chat.id, session_id)
            await message.reply(text_rep)
            await client.send_chat_action(message.chat.id, "cancel")
            message.continue_propagation()
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
                #print (rm)
                lan = translator.detect(rm)
            msg = rm
            test = msg
            if not "en" in lan and not lan == "":
                msg = translator.translate(test, lang_tgt="en")
            try:
                session_id = session.get("session_id")
                rep = api_client.think_thought(session_id, msg)
            except:
                 session = api_client.create_session()
                 session_id = session.id
                 rep = api_client.think_thought(session_id, msg)
                 update_session(message.chat.id, session_id)
            
            pro = rep
            if not "en" in lan and not lan == "":
                pro = translator.translate(rep, lang_tgt=lan[0])
            if message.chat.id in ws_chats:                    
                answer = pro
                try:
                    tts = gTTS(answer, tld="com", lang=lan[0])
                    tts.save("results.mp3")
                except AssertionError:
                    message.continue_propagation()
                except ValueError:
                    message.continue_propagation()
                except RuntimeError:
                    message.continue_propagation()
                except gTTSError:
                    message.continue_propagation()
                with open("results.mp3", "r"):
                    await pbot.send_voice(
                        message.chat.id,
                        "results.mp3",
                        reply_to_message_id=message.message_id,
                    )
                os.remove("results.mp3")          
            else:     
                await message.reply(pro)


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





#    Copyright (C) 2020-2021 by @InukaAsith
#    This programme is a part of DaisyX (TG bot) project
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.

#    Kang with the credits
