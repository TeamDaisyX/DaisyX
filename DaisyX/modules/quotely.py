from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError

from DaisyX.services.events import register
from DaisyX.services.telethonuserbot import ubot


@register(pattern="^/qbot$")
async def _(event):
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await event.reply("```Reply to any user message.```")
        return
    reply_message = await event.get_reply_message()
    chat = "@QuotLyBot"
    reply_message.sender
    if reply_message.sender.bot:
        await event.reply("```Reply to actual users message.```")
        return
    await event.reply("```Making a Quote```")
    async with ubot.conversation(chat) as conv:
        try:
            response = conv.wait_event(
                events.NewMessage(incoming=True, from_users=1031952739)
            )
            await ubot.forward_messages(chat, reply_message)
            response = await response
        except YouBlockedUserError:
            await event.reply("```Please unblock @QuotLyBot and try again```")
            return
        if response.text.startswith("Hi!"):
            await event.reply(
                "```Can you kindly disable your forward privacy settings for good?```"
            )
        else:
            await ubot.forward_messages(event.chat_id, response.message)
