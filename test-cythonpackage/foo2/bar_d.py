import sys

import cython

def print_me():
    if cython.compiled:
        print("foo2.bar_d compiled.")
        sys.exit(0)
    else:
        print("foo2.bar_d interpreted.")
        sys.exit(1)
