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

from pymongo import InsertOne

from DaisyX.services.mongo import mongodb
from DaisyX.utils.logger import log

log.info("Daisy Database v5")
log.info("Feds: migrate to old feds database structure")
log.info("Starting updating all feds...")

all_feds = mongodb.feds.find({})
all_feds_count = all_feds.count()
counter = 0
changed_feds = 0
for fed in all_feds:
    counter += 1
    log.info(f"Updating {counter} of {all_feds_count}...")

    queue = []
    if "banned" not in fed:
        continue

    for item in fed["banned"].items():
        user_id = item[0]
        ban = item[1]
        new = {
            "fed_id": fed["fed_id"],
            "user_id": user_id,
            "by": ban["by"],
            "time": ban["time"],
        }

        if "reason" in ban:
            new["reason"] = ban["reason"]

        if "banned_chats" in ban:
            new["banned_chats"] = ban["banned_chats"]

        queue.append(InsertOne(new))

    mongodb.fed_bans.bulk_write(queue)
    mongodb.feds.update_one({"fed_id": fed["fed_id"]}, {"$unset": {"banned": 1}})
    changed_feds += 1

log.info("Update done!")
log.info("Modified feds - " + str(changed_feds))
log.info("Unchanged feds - " + str(all_feds_count - changed_feds))
