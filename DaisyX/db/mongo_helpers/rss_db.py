from DaisyX.services.mongo import mongodb as db_x

rss = db_x["RSS"]


def add_rss(chat_id, rss_link, latest_rss):
    rss.insert_one({"chat_id": chat_id, "rss_link": rss_link, "latest_rss": latest_rss})


def del_rss(chat_id, rss_link):
    rss.delete_one({"chat_id": chat_id, "rss_link": rss_link})


def get_chat_rss(chat_id):
    return list(rss.find({"chat_id": chat_id}))


def update_rss(chat_id, rss_link, latest_rss):
    rss.update_one(
        {"chat_id": chat_id, "rss_link": rss_link}, {"$set": {"latest_rss": latest_rss}}
    )


def is_get_chat_rss(chat_id, rss_link):
    return bool(lol := rss.find_one({"chat_id": chat_id, "rss_link": rss_link}))


def basic_check(chat_id):
    return bool(lol := rss.find_one({"chat_id": chat_id}))


def overall_check():
    return bool(lol := rss.find_one())


def get_all():
    return rss.find()


def delete_all():
    rss.delete_many({})
