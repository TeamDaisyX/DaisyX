# Ported From William Butcher Bot :- https://github.com/thehamkercat/WilliamButcherBot/edit/dev/wbb/modules/webss.py .
# All Credit to WilliamButcherBot.


from pyrogram import filters

from DaisyX.function.pluginhelpers import admins_only
from DaisyX.services.pyrogram import pbot as app


@app.on_message(filters.command("webss") & ~filters.private & ~filters.edited)
@admins_only
async def take_ss(_, message):
    if len(message.command) != 2:
        await message.reply_text("Give A Url To Fetch Screenshot.")
        return
    url = message.text.split(None, 1)[1]
    m = await message.reply_text("**Taking Screenshot**")
    await m.edit("**Uploading**")
    try:
        await app.send_photo(
            message.chat.id,
            photo=f"https://webshot.amanoteam.com/print?q={url}",
        )
    except TypeError:
        await m.edit("No Such Website.")
        return
    await m.delete()
