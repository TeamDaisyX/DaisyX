# Support Dual Mongo DB now
# For free users

from motor.motor_asyncio import AsyncIOMotorClient as MongoClient

from DaisyX.config import get_str_key

MONGO2 = get_str_key("MONGO_URI_2", None)
MONGO = get_str_key("MONGO_URI", required=True)
if MONGO2 is None:
    MONGO2 = MONGO

mongo_client = MongoClient(MONGO2)
db = mongo_client.daisy
