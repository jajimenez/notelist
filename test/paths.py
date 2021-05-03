"""Module to insert the "src" directory in "sys.path"."""

import sys
from os.path import dirname, abspath, realpath, join


_dir = dirname(abspath(__file__))
_src_dir = realpath(join(_dir, "..", "src"))

sys.path.insert(0, _src_dir)
