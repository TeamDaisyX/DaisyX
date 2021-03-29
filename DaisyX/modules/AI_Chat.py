
#    Copyright (C) 2020-2021 by @AmarnathCdj & @InukaAsith
#    Chatbot system written by @AmarnathCdj databse added and recoded for pyrogram by @InukaAsith
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
#    Special credits to @AmarnathCdj

import emoji
import requests
url = "https://iamai.p.rapidapi.com/ask"
from DaisyX import OWNER_ID, BOT_ID
from DaisyX.services.pyrogram import pbot as daisyx
from pyrogram import filters
import asyncio, os
from DaisyX.function.pluginhelpers import admins_only
from json import JSONDecodeError
import json
from google_trans_new import google_translator

daisy_chats = []
sin_chats = []
# AI Chat (C) 2020-2021 by @InukaAsith

@daisyx.on_message(filters.command("chatbot") & ~filters.edited & ~filters.bot)
@admins_only
async def hmm(_, message):
    global daisy_chats
    if len(message.command) != 2:
        await message.reply_text("I only recognize `/chatbot on` and /chatbot `off only`")
        return
    status = message.text.split(None, 1)[1] 
    chat_id = message.chat.id
    if status == "ON" or status == "on" or status == "On":
        if chat_id not in daisy_chats:
            daisy_chats.append(message.chat.id)
            text = "Chatbot Enabled Reply To Any Message" \
                   + "Of Daisy To Get A Reply"
            await message.reply_text(text)
            return
        await message.reply_text("ChatBot Is Already Enabled.")
        return

    elif status == "OFF" or status == "off" or status == "Off":
        if chat_id in daisy_chats:
            daisy_chats.remove(chat_id)
            await message.reply_text("AI chat Disabled!")
            return
        await message.reply_text("AI Chat Is Already Disabled.")
        return
    elif status == "si" or status == "sinhala" or status == "sin":
        if chat_id not in daisy_chats:
            daisy_chats.append(message.chat.id)
            sin_chats.append(message.chat.id)
            text = "Chatbot Enabled Reply To Any Message" \
                   + "Of Daisy To Get A Reply"
            await message.reply_text(text)
            return
        await message.reply_text("ChatBot Is Already Enabled.")
        return
    else:
        await message.reply_text("I only recognize `/chatbot on` and /chatbot `off only`")



@daisyx.on_message(filters.text & filters.reply & ~filters.bot &
        ~filters.via_bot & ~filters.forwarded  & ~filters.command("whois") & ~filters.command("spwinfo") ,group=2)
async def hmm(client,message):
  if message.chat.id not in daisy_chats:
    return
  if message.reply_to_message.from_user.id != BOT_ID:
    return
  if message.chat.id in sin_chats:
    lan = "si"
    print("si")
  else:
    lan = "en"
  test = message.text
  if test.startswith("/") or test.startswith("@"):
    return
  translator = google_translator()
  test = emoji.demojize(test.strip())
  
# Kang with the credits bitches @InukaASiTH

  try:
    test = test.replace('daisy', 'Jessica')
  except:
    return
  r = ('\n    \"consent\": true,\n    \"ip\": \"::1\",\n    \"question\": \"{}\"\n').format(test)
  k = f"({r})"
  new_string = k.replace("(", "{")
  lol = new_string.replace(")","}")
  payload = lol
  headers = {
      'content-type': "application/json",
      'x-forwarded-for': "<user's ip>",
      'x-rapidapi-key': "33b8b1a671msh1c579ad878d8881p173811jsn6e5d3337e4fc",
      'x-rapidapi-host': "iamai.p.rapidapi.com"
      }
 
  response = requests.request("POST", url, data=payload, headers=headers)
  lodu = response.json()
  result = (lodu['message']['text'])
  pro = translator.translate(result, lang_tgt=lan)
  pro = pro.replace('Thergiakis Eftichios','@InukaAsith')
  pro = pro.replace('Jessica','Daisy')
  if "Out of all ninja turtle" in result:
   pro = "Sorry! looks I missed that. I'm at your service ask anthing sir?"
   try:
      await daisyx.send_chat_action(message.chat.id, "typing")
      await message.reply_text(pro)
   except CFError as e:
           print(e)
  elif "ann" in result:
   pro = "My name is Daisy"
   try:
      await daisyx.send_chat_action(message.chat.id, "typing")
      await message.reply_text(pro)
   except CFError as e:
           print(e)
  else:
    try:
      await daisyx.send_chat_action(message.chat.id, "typing")
      await message.reply_text(pro)
    except CFError as e:
           print(e)
  

@daisyx.on_message(filters.text & filters.private & filters.reply & ~filters.bot &
        ~filters.via_bot & ~filters.forwarded)
async def inuka(client,message):
  test = message.text
  if test.startswith("/") or test.startswith("@"):
     return
  test = emoji.demojize(test.strip())
  if "daisy" in test or 'Daisy' in test:
    try:
      test = test.replace('daisy', 'Jessica')
    except:
      test = test.replace('Daisy', 'Jessica')
  r = ('\n    \"consent\": true,\n    \"ip\": \"::1\",\n    \"question\": \"{}\"\n').format(test)
  k = f"({r})"
  new_string = k.replace("(", "{")
  lol = new_string.replace(")","}")
  payload = lol
  headers = {
    'content-type': "application/json",
    'x-forwarded-for': "<user's ip>",
    'x-rapidapi-key': "33b8b1a671msh1c579ad878d8881p173811jsn6e5d3337e4fc",
    'x-rapidapi-host': "iamai.p.rapidapi.com"
    }

  response = requests.request("POST", url, data=payload, headers=headers)
  lodu = response.json()
  result = (lodu['message']['text'])
  pro = result
  pro = pro.replace('Thergiakis Eftichios','@InukaAsith')
  pro = pro.replace('Jessica','Daisy')
  if "Out of all ninja" in result:
   pro = "Sorry! I missed that. How can I help you ?"
   try:
      await daisyx.send_chat_action(message.chat.id, "typing")
      await message.reply_text(pro)
   except CFError as e:
           print(e)
  elif "ann" in result:
   pro = "My name is Daisy"
   try:
      await daisyx.send_chat_action(message.chat.id, "typing")
      await message.reply_text(pro)
   except CFError as e:
           print(e)
  else:
    try:
      await daisyx.send_chat_action(message.chat.id, "typing")
      await message.reply_text(result)
    except CFError as e:
           print(e)

@daisyx.on_message(filters.regex("Daisy|daisy|DaisyX|daisyx|Daisyx") & ~filters.bot &
        ~filters.via_bot & ~filters.forwarded & ~filters.reply & ~filters.channel  & ~filters.command("whois") & ~filters.command("spwinfo") ,group=1)
async def inuka(client,message):
  test = str(message.text)
  if test.startswith("/") or test.startswith("@"):
    return
  test = emoji.demojize(test.strip())
  if "daisy" in test or 'Daisy' in test:
    try:
      test = test.replace('daisy', 'Jessica')
    except:
      test = test.replace('Daisy', 'Jessica')
    r = ('\n    \"consent\": true,\n    \"ip\": \"::1\",\n    \"question\": \"{}\"\n').format(test)
    k = f"({r})"
    new_string = k.replace("(", "{")
    lol = new_string.replace(")","}")
    payload = lol
    headers = {
      'content-type': "application/json",
      'x-forwarded-for': "<user's ip>",
      'x-rapidapi-key': "33b8b1a671msh1c579ad878d8881p173811jsn6e5d3337e4fc",
      'x-rapidapi-host': "iamai.p.rapidapi.com"
      }

    response = requests.request("POST", url, data=payload, headers=headers)
    lodu = response.json()
    result = (lodu['message']['text'])
    pro = result
    pro = pro.replace('Thergiakis Eftichios','@InukaAsith')
    pro = pro.replace('Jessica','Daisy')
    if "Out of all ninja" in result:
     pro = "Sorry! I missed that. How can I help you ?"
     try:
        await daisyx.send_chat_action(message.chat.id, "typing")
        await message.reply_text(pro)
     except CFError as e:
             print(e)
    elif "ann" in result:
     pro = "My name is Daisy"
     try:
        await daisyx.send_chat_action(message.chat.id, "typing")
        await message.reply_text(pro)
     except CFError as e:
             print(e)
    else:
      try:
        await daisyx.send_chat_action(message.chat.id, "typing")
        await message.reply_text(result)
      except CFError as e:
             print(e)
