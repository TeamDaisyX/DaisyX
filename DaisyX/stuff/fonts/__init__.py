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


def list_all_fonts():
    import glob
    from os.path import basename, dirname, isfile

    mod_paths = glob.glob(f"{dirname(__file__)}/*.ttf")
    return [
        f"{dirname(f)}/{basename(f)}"
        for f in mod_paths
        if isfile(f) and f.endswith(".ttf")
    ]


ALL_FONTS = sorted(list_all_fonts())
__all__ = ALL_FONTS + ["ALL_FONTS"]
