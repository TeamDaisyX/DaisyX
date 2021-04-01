import pymongo

from DaisyX.config import get_str_key

MONGO2 = get_str_key("FILTERS_MONGO", None)
MONGO = get_str_key("MONGO_URI", required=True)
if MONGO2 == None:
    MONGO2 = MONGO
myclient = pymongo.MongoClient(MONGO2)
mydb = myclient["Daisy"]
mycol = mydb["USERS"]


async def add_user(id, username, name, dcid):
    data = {"_id": id, "username": username, "name": name, "dc_id": dcid}
    try:
        mycol.update_one({"_id": id}, {"$set": data}, upsert=True)
    except:
        pass


async def all_users():
    count = mycol.count()
    return count


async def find_user(id):
    query = mycol.find({"_id": id})

    try:
        for file in query:
            name = file["name"]
            username = file["username"]
            dc_id = file["dc_id"]
        return name, username, dc_id
    except:
        return None, None, None
