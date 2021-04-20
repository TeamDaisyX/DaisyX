
from pyrogram import filters
from DaisyX.services.pyrogram import pbot
from DaisyX.function.pluginhelpers import admins_only

@pbot.on_message(filters.command("invitelink") & ~filters.edited & ~filters.bot)
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
