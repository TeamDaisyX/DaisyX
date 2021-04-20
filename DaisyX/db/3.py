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

from DaisyX.services.mongo import mongodb
from DaisyX.utils.logger import log

log.info("Daisy Database v3")
log.info("Support notes aliases")
log.info("Starting updating all notes...")

all_notes = mongodb.notes_v2.find({})
all_notes_count = all_notes.count()
counter = 0
changed_notes = 0
for note in all_notes:
    counter += 1
    log.info(f"Updating {counter} of {all_notes_count}...")

    if "name" in note:
        changed_notes += 1
        names = [note["name"]]
        del note["name"]
        note["names"] = names
        mongodb.notes_v2.replace_one({"_id": note["_id"]}, note)

log.info("Update done!")
log.info("Modified notes - " + str(changed_notes))
log.info("Unchanged notes - " + str(all_notes_count - changed_notes))
