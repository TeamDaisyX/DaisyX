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

log.info("Daisy Database v6")
log.info("Filters: migrate 'reply_message'")
log.info("Starting to updating all filters...")

all_filters = mongodb.filters.find({"action": "reply_message"})
count = all_filters.count()
changed = 0
updated_list = []

for i in all_filters:
    if not isinstance(i["reply_text"], dict):
        changed += 1
        log.info(f"Updated {changed} filters of {count}")
        updated_list.append(
            UpdateOne(
                {"_id": i["_id"]},
                {"$set": {"reply_text": {"parse_mode": "md", "text": i["reply_text"]}}},
            )
        )

log.info("Updating Database ...")
if updated_list:
    mongodb.filters.bulk_write(updated_list)
