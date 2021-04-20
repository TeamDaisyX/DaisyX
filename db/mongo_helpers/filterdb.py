from typing import Dict, List, Union

from DaisyX.services.mongo2 import db

filtersdb = db.filters


""" Filters funcions """


async def _get_filters(chat_id: int) -> Dict[str, int]:
    _filters = await filtersdb.find_one({"chat_id": chat_id})
    if _filters:
        _filters = _filters["filters"]
    else:
        _filters = {}
    return _filters


async def get_filters_names(chat_id: int) -> List[str]:
    _filters = []
    for _filter in await _get_filters(chat_id):
        _filters.append(_filter)
    return _filters


async def get_filter(chat_id: int, name: str) -> Union[bool, dict]:
    name = name.lower().strip()
    _filters = await _get_filters(chat_id)
    if name in _filters:
        return _filters[name]
    else:
        return False


async def save_filter(chat_id: int, name: str, _filter: dict):
    name = name.lower().strip()
    _filters = await _get_filters(chat_id)
    _filters[name] = _filter

    await filtersdb.update_one(
        {"chat_id": chat_id}, {"$set": {"filters": _filters}}, upsert=True
    )


async def delete_filter(chat_id: int, name: str) -> bool:
    filtersd = await _get_filters(chat_id)
    name = name.lower().strip()
    if name in filtersd:
        del filtersd[name]
        await filtersdb.update_one(
            {"chat_id": chat_id}, {"$set": {"filters": filtersd}}, upsert=True
        )
        return True
    return False
