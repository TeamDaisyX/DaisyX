# This file is part of Daisy (Telegram Bot)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import asyncio
import functools
import pickle
from typing import Optional, Union

from DaisyX.services.redis import bredis
from DaisyX.utils.logger import log


async def set_value(key, value, ttl):
    value = pickle.dumps(value)
    bredis.set(key, value)
    if ttl:
        bredis.expire(key, ttl)


class cached:
    def __init__(
        self,
        ttl: Optional[Union[int, float]] = None,
        key: Optional[str] = None,
        no_self: bool = False,
    ):
        self.ttl = ttl
        self.key = key
        self.no_self = no_self

    def __call__(self, *args, **kwargs):
        if not hasattr(self, "func"):
            self.func = args[0]
            # wrap
            functools.update_wrapper(self, self.func)
            # return ``cached`` object when function is not being called
            return self
        return self._set(*args, **kwargs)

    async def _set(self, *args: dict, **kwargs: dict):
        key = self.__build_key(*args, **kwargs)

        if bredis.exists(key):
            value = pickle.loads(bredis.get(key))
            return value if type(value) is not _NotSet else value.real_value

        result = await self.func(*args, **kwargs)
        if result is None:
            result = _NotSet()
        asyncio.ensure_future(set_value(key, result, ttl=self.ttl))
        log.debug(f"Cached: writing new data for key - {key}")
        return result if type(result) is not _NotSet else result.real_value

    def __build_key(self, *args: dict, **kwargs: dict) -> str:
        ordered_kwargs = sorted(kwargs.items())

        new_key = self.key or (self.func.__module__ or "") + self.func.__name__
        new_key += str(args[1:] if self.no_self else args)

        if ordered_kwargs:
            new_key += str(ordered_kwargs)

        return new_key

    async def reset_cache(self, *args, new_value=None, **kwargs):
        """
        >>> @cached()
        >>> def somefunction(arg):
        >>>     pass
        >>>
        >>> [...]
        >>> arg = ... # same thing ^^
        >>> await somefunction.reset_cache(arg, new_value='Something')

        :param new_value: new/ updated value to be set [optional]
        """

        key = self.__build_key(*args, **kwargs)
        if new_value:
            return set_value(key, new_value, ttl=self.ttl)
        return bredis.delete(key)


class _NotSet:
    real_value = None

    def __repr__(self) -> str:
        return "NotSet"
