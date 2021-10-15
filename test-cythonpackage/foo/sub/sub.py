import sys

import cython

def print_me():
    if cython.compiled:
        print("foo.sub.sub compiled.")
        sys.exit(0)
    else:
        print("foo.sub.sub interpreted.")
        sys.exit(1)
