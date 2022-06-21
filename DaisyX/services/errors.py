import sys
import traceback
from functools import wraps

from DaisyX import SUPPORT_CHAT
from DaisyX.services.pyrogram import pbot


def split_limits(text):
    if len(text) < 2048:
        return [text]

    lines = text.splitlines(True)
    small_msg = ""
    result = []
    for line in lines:
        if len(small_msg) + len(line) < 2048:
            small_msg += line
        else:
            result.append(small_msg)
            small_msg = line
    result.append(small_msg)

    return result


def capture_err(func):
    @wraps(func)
    async def capture(client, message, *args, **kwargs):
        try:
            return await func(client, message, *args, **kwargs)
        except Exception as err:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            errors = traceback.format_exception(
                etype=exc_type,
                value=exc_obj,
                tb=exc_tb,
            )
            error_feedback = split_limits(
                f'**ERROR** | `{message.from_user.id if message.from_user else 0}` | `{message.chat.id if message.chat else 0}`\n\n```{message.text or message.caption}```\n\n```{"".join(errors)}```\n'
            )

            for x in error_feedback:
                await pbot.send_message(SUPPORT_CHAT, x)
            raise err

    return capture
