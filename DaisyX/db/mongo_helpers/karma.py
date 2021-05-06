from DaisyX.services.mongo2 import db

karmadb = db.karma2


async def is_karma_on(chat_id: int) -> bool:
    chat = await karmadb.find_one({"chat_id": chat_id})
    if not chat:
        return False
    return True


async def karma_on(chat_id: int):
    is_karma = await is_karma_on(chat_id)
    if is_karma:
        return
    return await karmadb.insert_one({"chat_id": chat_id})


async def karma_off(chat_id: int):
    is_karma = await is_karma_on(chat_id)
    if not is_karma:
        return
    return await karmadb.delete_one({"chat_id": chat_id})
