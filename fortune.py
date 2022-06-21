import codecs
import random
import re
import sys
from optparse import OptionParser

# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

__all__ = ["main", "get_random_fortune"]

# Info about the module
__version__ = "1.1.0"
__author__ = "Brian M. Clapper"
__email__ = "bmc@clapper.org"
__url__ = "http://software.clapper.org/fortune/"
__copyright__ = "2008-2019 Brian M. Clapper"
__license__ = "BSD-style license"

# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


def _random_int(start, end):
    try:
        # Use SystemRandom, if it's available, since it's likely to have
        # more entropy.
        r = random.SystemRandom()
    except BaseException:
        r = random

    return r.randint(start, end)


def _read_fortunes(fortune_file):
    with codecs.open(fortune_file, mode="r", encoding="utf-8") as f:
        contents = f.read()

    lines = [line.rstrip() for line in contents.split("\n")]

    delim = re.compile(r"^%$")

    fortunes = []
    cur = []

    def save_if_nonempty(buf):
        fortune = "\n".join(buf)
        if fortune.strip():
            fortunes.append(fortune)

    for line in lines:
        if delim.match(line):
            save_if_nonempty(cur)
            cur = []
            continue

        cur.append(line)

    if cur:
        save_if_nonempty(cur)

    return fortunes


def get_random_fortune(fortune_file):
    fortunes = list(_read_fortunes(fortune_file))
    randomRecord = _random_int(0, len(fortunes) - 1)
    return fortunes[randomRecord]


def main():
    usage = "Usage: %prog [OPTIONS] [fortune_file]"
    arg_parser = OptionParser(usage=usage)
    arg_parser.add_option(
        "-V",
        "--version",
        action="store_true",
        dest="show_version",
        help="Show version and exit.",
    )
    arg_parser.epilog = (
        "If fortune_file is omitted, fortune looks at the "
        "FORTUNE_FILE environment variable for the path."
    )

    options, args = arg_parser.parse_args(sys.argv)
    if len(args) == 2:
        fortune_file = args[1]

    else:
        try:
            fortune_file = "notes.txt"
        except KeyError:
            print("Missing fortune file.", file=sys.stderr)
            print(usage, file=sys.stderr)
            sys.exit(1)

    try:
        if options.show_version:
            print(f"fortune, version {__version__}")
        else:
            print(get_random_fortune(fortune_file))
    except ValueError as msg:
        print(msg, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
