from DaisyX.services.mongo import mongodb as db_x

lydia = db_x["CAHTBOT"]


def add_chat(chat_id):
    if stark := lydia.find_one({"chat_id": chat_id}):
        return False
    lydia.insert_one({"chat_id": chat_id})
    return True


def remove_chat(chat_id):
    if stark := lydia.find_one({"chat_id": chat_id}):
        lydia.delete_one({"chat_id": chat_id})
        return True
    else:
        return False


def get_all_chats():
    return r if (r := list(lydia.find())) else False


def get_session(chat_id):
    stark = lydia.find_one({"chat_id": chat_id})
    return stark or False
