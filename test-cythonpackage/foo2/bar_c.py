import sys

import cython

def print_me():
    if cython.compiled:
        print("foo2.bar_c compiled.")
        sys.exit(0)
    else:
        print("foo2.bar_c interpreted.")
        sys.exit(1)
