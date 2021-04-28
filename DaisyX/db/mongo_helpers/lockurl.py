from DaisyX.services.mongo import mongodb as db_x

lockurl = db_x["Lockurlp"]


def add_chat(chat_id):
    stark = lockurl.find_one({"chat_id": chat_id})
    if stark:
        return False
    else:
        lockurl.insert_one({"chat_id": chat_id})
        return True


def remove_chat(chat_id):
    stark = lockurl.find_one({"chat_id": chat_id})
    if not stark:
        return False
    else:
        lockurl.delete_one({"chat_id": chat_id})
        return True


def get_all_chats():
    r = list(lockurl.find())
    if r:
        return r
    else:
        return False


def get_session(chat_id):
    stark = lockurl.find_one({"chat_id": chat_id})
    if not stark:
        return False
    else:
        return stark
