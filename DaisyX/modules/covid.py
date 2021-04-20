# for Porting This Module You Need to Port pyroplugs ( folder) with errors.py, json_prettify.py, fetch.py

from pyrogram import filters

from DaisyX.function.pluginhelpers import fetch, json_prettify
from DaisyX.services.pyrogram import pbot as app


@app.on_message(filters.command("covid") & ~filters.edited)
async def covid(_, message):
    if len(message.command) == 1:
        data = await fetch("https://corona.lmao.ninja/v2/all")
        data = await json_prettify(data)
        await app.send_message(message.chat.id, text=data)
        return
    if len(message.command) != 1:
        country = message.text.split(None, 1)[1].strip()
        country = country.replace(" ", "")
        data = await fetch(f"https://corona.lmao.ninja/v2/countries/{country}")
        data = await json_prettify(data)
        await app.send_message(message.chat.id, text=data)
        return
