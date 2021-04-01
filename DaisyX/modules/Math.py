# Written by Inukaasith for the Daisy project
# This file is part of DaisyXBot (Telegram Bot)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.


import io
import json
import math
import sys
import traceback

import requests

from DaisyX.decorator import register
from DaisyX.services.events import register as daisy

from .utils.disable import disableable_dec
from .utils.message import get_args_str


@daisy(pattern="^/math (.*)")
async def _(car):
    if car.fwd_from:
        return
    cmd = car.text.split(" ", maxsplit=1)[1]
    event = await car.reply("Calculating ...")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    san = f"print({cmd})"
    try:
        await aexec(san, event)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Sorry Daisy can't find result for the given equation"
    final_output = "**EQUATION**: `{}` \n\n **SOLUTION**: \n`{}` \n".format(
        cmd, evaluation
    )
    await event.edit(final_output)


async def aexec(code, event):
    exec(f"async def __aexec(event): " + "".join(f"\n {l}" for l in code.split("\n")))
    return await locals()["__aexec"](event)


@register(cmds=["factor", "factorize"])
@disableable_dec("factor")
async def _(message):
    args = get_args_str(message)
    response = requests.get(f"https://newton.now.sh/api/v2/factor/{args}")
    c = response.text
    obj = json.loads(c)
    j = obj["result"]
    await message.reply(j)


@register(cmds="derive")
@disableable_dec("derive")
async def _(message):
    args = get_args_str(message)
    response = requests.get(f"https://newton.now.sh/api/v2/derive/{args}")
    c = response.text
    obj = json.loads(c)
    j = obj["result"]
    await message.reply(j)


@register(cmds="integrate")
@disableable_dec("integrate")
async def _(message):
    args = get_args_str(message)
    response = requests.get(f"https://newton.now.sh/api/v2/integrate/{args}")
    c = response.text
    obj = json.loads(c)
    j = obj["result"]
    await message.reply(j)


@register(cmds="zeroes")
@disableable_dec("zeroes")
async def _(message):
    args = get_args_str(message)
    response = requests.get(f"https://newton.now.sh/api/v2/zeroes/{args}")
    c = response.text
    obj = json.loads(c)
    j = obj["result"]
    await message.reply(j)


@register(cmds="tangent")
@disableable_dec("tangent")
async def _(message):
    args = get_args_str(message)
    response = requests.get(f"https://newton.now.sh/api/v2/tangent/{args}")
    c = response.text
    obj = json.loads(c)
    j = obj["result"]
    await message.reply(j)


@register(cmds="area")
@disableable_dec("area")
async def _(message):
    args = get_args_str(message)
    response = requests.get(f"https://newton.now.sh/api/v2/area/{args}")
    c = response.text
    obj = json.loads(c)
    j = obj["result"]
    await message.reply(j)


@register(cmds="cos")
@disableable_dec("cos")
async def _(message):
    args = get_args_str(message)
    await message.reply(str(math.cos(int(args))))


@register(cmds="sin")
@disableable_dec("sin")
async def _(message):
    args = get_args_str(message)
    await message.reply(str(math.sin(int(args))))


@register(cmds="tan")
@disableable_dec("tan")
async def _(message):
    args = get_args_str(message)
    await message.reply(str(math.tan(int(args))))


@register(cmds="arccos")
@disableable_dec("arccos")
async def _(message):
    args = get_args_str(message)
    await message.reply(str(math.acos(int(args))))


@register(cmds="arcsin")
@disableable_dec("arcsin")
async def _(message):
    args = get_args_str(message)
    await message.reply(str(math.asin(int(args))))


@register(cmds="arctan")
@disableable_dec("arctan")
async def _(message):
    args = get_args_str(message)
    await message.reply(str(math.atan(int(args))))


@register(cmds="abs")
@disableable_dec("abs")
async def _(message):
    args = get_args_str(message)
    await message.reply(str(math.fabs(int(args))))


@register(cmds="log")
@disableable_dec("log")
async def _(message):
    args = get_args_str(message)
    await message.reply(str(math.log(int(args))))


__help__ = """
Solves complex math problems using https://newton.now.sh and python math module
 - /simplify- Math /math 2^2+2(2)
 - /factor - Factor /factor x^2 + 2x
 - /derive - Derive /derive x^2+2x
 - /integrate - Integrate /integrate x^2+2x
 - /zeroes - Find 0's /zeroes x^2+2x
 - /tangent - Find Tangent /tangent 2lx^
 - /area - Area Under Curve /area 2:4lx^3`
 - /cos - Cosine /cos pi
 - /sin - Sine /sin 0
 - /tan - Tangent /tan 0
 - /arccos - Inverse Cosine /arccos 1
 - /arcsin - Inverse Sine /arcsin 0
 - /arctan - Inverse Tangent /arctan 0
 - /abs - Absolute Value /abs -1
 - /log* - Logarithm /log 2l8
 
Keep in mind, To find the tangent line of a function at a certain x value, send the request as c|f(x) where c is the given x value and f(x) is the function expression, the separator is a vertical bar '|'. See the table above for an example request.
To find the area under a function, send the request as c:d|f(x) where c is the starting x value, d is the ending x value, and f(x) is the function under which you want the curve between the two x values.
To compute fractions, enter expressions as numerator(over)denominator. For example, to process 2/4 you must send in your expression as 2(over)4. The result expression will be in standard math notation (1/2, 3/4).
"""

__mod_name__ = "Maths"
