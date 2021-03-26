
import os
from DaisyX.services.telethon import tbot
from time import time

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


LYDIA_API_KEY = get_str_key("LYDIA_API_KEY", required=False)
CoffeeHouseAPI = API(LYDIA_API_KEY)
api_client = LydiaAI(CoffeeHouseAPI)


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
    user = await tbot.get_entity(send)
    is_chat = sql.is_chat(chat.id)
    if not is_chat:
        ses = api_client.create_session()
        ses_id = str(ses.id)
        expires = str(ses.expires)
        sql.set_ses(chat.id, ses_id, expires)
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
    user = await tbot.get_entity(send)
    is_chat = sql.is_chat(chat.id)
    if not is_chat:
        await event.reply("AI isn't enabled here in the first place!")
        return ""
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
    if msg:
        if not await check_message(event):
            return
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
            
__help__ = """
<b> Chatbot </b>
 - /chatbot <i>ON/OFF</i>: Enables and disables AI Chat mode (EXCLUSIVE)
 - /addlydia: Activates lydia on your group (UNSTABLE)
 - /rmlydia : Deactivates lydia on your group (UNSTABLE)
 
<b> Assistant </b>
 - /ask <i>question</i>: Ask question from daisy
 - /ask <i> reply to voice note</i>: Get voice reply
<i>Special credits to Julia project (Voice ai) and FridayUserbot</i>
"""

__mod_name__ = "AI Assistant"           
