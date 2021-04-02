from DaisyX.services.mongo import mongodb as db_x

rss = db_x["RSS"]


async def add_rss(chat_id, rss_link, latest_rss):
    await rss.insert_one(
        {"chat_id": chat_id, "rss_link": rss_link, "latest_rss": latest_rss}
    )


async def del_rss(chat_id, rss_link):
    await rss.delete_one({"chat_id": chat_id, "rss_link": rss_link})


async def get_chat_rss(chat_id):
    lol = [m async for m in rss.find({"chat_id": chat_id})]
    return lol


async def update_rss(chat_id, rss_link, latest_rss):
    await rss.update_one(
        {"chat_id": chat_id, "rss_link": rss_link}, {"$set": {"latest_rss": latest_rss}}
    )


async def is_get_chat_rss(chat_id, rss_link):
    lol = await rss.find_one({"chat_id": chat_id, "rss_link": rss_link})
    if lol:
        return True
    else:
        return False


async def basic_check(chat_id):
    lol = await rss.find_one({"chat_id": chat_id})
    if lol:
        return True
    else:
        return False


async def overall_check():
    lol = await rss.find_one()
    if lol:
        return True
    else:
        return False


async def get_all():
    lol = [rrrs async for rrrs in rss.find()]
    return lol


async def delete_all():
    await rss.delete_many({})
