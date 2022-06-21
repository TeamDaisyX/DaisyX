from DaisyX.services.mongo import mongodb as db_x

lockurl = db_x["Lockurlp"]


def add_chat(chat_id):
    if stark := lockurl.find_one({"chat_id": chat_id}):
        return False
    lockurl.insert_one({"chat_id": chat_id})
    return True


def remove_chat(chat_id):
    if stark := lockurl.find_one({"chat_id": chat_id}):
        lockurl.delete_one({"chat_id": chat_id})
        return True
    else:
        return False


def get_all_chats():
    return r if (r := list(lockurl.find())) else False


def get_session(chat_id):
    stark = lockurl.find_one({"chat_id": chat_id})
    return stark or False
