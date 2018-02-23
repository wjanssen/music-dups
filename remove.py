"""
Remove all files listed in file given as first argument on command-line.

Basically, "cat ARG | xargs rm -vf".
"""

import sys, re, os, shutil, tarfile

rmfile = open(sys.argv[1])
for filename in rmfile.readlines():
    filename = filename.strip()
    if os.path.exists(filename):
        os.unlink(filename)
        print filename
