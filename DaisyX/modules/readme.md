## DaisyX Example plugin
```python3

from DaisyX.decorator import register
from .utils.disable import disableable_dec
from .utils.message import get_args_str

@register(cmds="Hi")
@disableable_dec("Hi")
async def _(message):
    j = "Hello there"
    await message.reply(j)
```
