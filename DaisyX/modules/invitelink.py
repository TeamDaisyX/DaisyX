from pyrogram import filters

from DaisyX.function.pluginhelpers import admins_only
from DaisyX.services.pyrogram import pbot

__HELP__ = """
Classic filters are just like marie's filter system. If you still like that kind of filter system
**Admin Only**
 - /cfilter <word> <message>: Every time someone says "word", the bot will reply with "message"
You can also include buttons in filters, example send `/savefilter google` in reply to `Click Here To Open Google | [Button.url('Google', 'google.com')]`
 - /stopcfilter <word>: Stop that filter.
 - /stopallcfilters: Delete all filters in the current chat.
**Admin+Non-Admin**
 - /cfilters: List all active filters in the chat
 
 **Please note classic filters can be unstable. We recommend you to use /addfilter**
"""


@pbot.on_message(
    filters.command("invitelink") & ~filters.edited & ~filters.bot & ~filters.private
)
@admins_only
async def invitelink(client, message):
    chid = message.chat.id
    try:
        invitelink = await client.export_chat_invite_link(chid)
    except:
        await message.reply_text(
            "Add me as admin of yor group first",
        )
        return
    await message.reply_text(f"Invite link generated successfully \n\n {invitelink}")


@pbot.on_message(filters.command("cfilterhelp") & ~filters.private & ~filters.edited)
@admins_only
async def filtersghelp(client, message):
    await client.send_message(message.chat.id, text=__HELP__)
