import sys

import cython

def print_me():
    if cython.compiled:
        print("foo.bar_b compiled.")
        sys.exit(0)
    else:
        print("foo.bar_a interpreted.")
        sys.exit(1)
