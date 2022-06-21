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

import glob
import os.path


def list_all_filters():
    mod_paths = glob.glob(f"{os.path.dirname(__file__)}/*.py")
    return [
        os.path.basename(f)[:-3]
        for f in mod_paths
        if os.path.isfile(f)
        and f.endswith(".py")
        and not f.endswith("__init__.py")
    ]


ALL_FILTERS = sorted(list(list_all_filters()))

__all__ = ALL_FILTERS + ["ALL_FILTERS"]
