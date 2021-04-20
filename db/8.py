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

from pymongo import UpdateOne

from DaisyX.services.mongo import mongodb
from DaisyX.utils.logger import log

changelog = """
    Daisy database v8
    Warns: Change serialization method of warnmodes (time based)
    """
log.info(changelog)
log.info("Fetching all documents needed to update (in 'warnmode' collection)!")

data = mongodb["warnmode"].find({"time": {"$exists": True}})
count = data.count()
changed, deleted = 0, 0
updated_list = []


def _convert_time(__t: dict) -> str:
    from datetime import timedelta

    sec = timedelta(**__t).total_seconds()
    # this works on basis that days, hours, minutes are whole numbers!
    # check days first
    if sec % 86400 == 0:
        return f"{round(sec / 86400)}d"
    elif sec % 3600 == 0:
        # check hours
        return f"{round(sec / 3600)}h"
    elif sec % 60 == 0:
        # check minutes
        return f"{round(sec / 60)}m"
    else:
        log.warning(f"Found unexpected value {sec}...!")


for i in data:
    time = i["time"]
    if new_t := _convert_time(time):
        updated_list.append(UpdateOne({"_id": i["_id"]}, {"$set": {"time": new_t}}))
        changed += 1
    else:
        # deleted += 1
        # updated_list.append(DeleteOne({'_id': i['_id']}))
        pass

if updated_list:
    log.info("Updating database...")
    mongodb["warnmode"].bulk_write(updated_list, ordered=False)
    log.info(f"Updated {changed} documents!")
