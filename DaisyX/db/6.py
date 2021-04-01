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

from pymongo import DeleteOne

from DaisyX.services.mongo import mongodb
from DaisyX.utils.logger import log

log.info("Daisy Database v6")
log.info("Feds: fix str user_id and fix duplications")
log.info("Starting updating all feds...")

queue = []

all_bans = mongodb.fed_bans.find({"user_id": {"$type": "string"}})
all_bans_count = all_bans.count()
counter = 0
changed_feds = 0

for ban in all_bans:
    counter += 1
    changed_feds += 1
    queue.append(DeleteOne({"_id": ban["_id"]}))

mongodb.fed_bans.bulk_write(queue)

log.info("Update done!")
log.info("Modified feds - " + str(changed_feds))
