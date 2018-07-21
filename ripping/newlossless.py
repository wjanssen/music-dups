#!/usr/bin/env python
#
# Copy newly ripped music from iTunes artist/folder to somewhere else
#

import sys, os, os.path, time, shutil, re


TROUBLESOME_FILENAME_CHARS = re.compile(r'[^-\._0-9A-Za-z]')


def usage(msg=None):
    if msg:
        sys.stderr.write(msg + "\n")
    sys.stderr.write("Usage: python %s <root-directory> <age-in-days> [NEW-LOCATION=<dir> (default: None)] [EXTENSION=<file-extension> (default: m4a)]\n" % (sys.argv[0],))
    sys.exit(1)

def main(argv):
    if len(argv) < 3:
        usage()
    elif not os.path.isdir(argv[1]):
        usage("Specified <root-directory> %s is not a directory!\n" % (argv[1],))
    try:
        start_time = time.time() - float(argv[2]) * 24 * 60 * 60
    except:
        usage("<age-in-days> must be a number!")
    new_location = None         # don't copy it
    extension = ".m4a"          # default Apple Lossless format
    for arg in argv[3:]:
        if arg.startswith("EXTENSION="):
            extension = '.' + arg[len("EXTENSION="):]
        elif arg.startswith("NEW-LOCATION="):
            new_location = arg[len("NEW-LOCATION="):]

    for dirpath, dirnames, filenames in os.walk(os.path.abspath(argv[1])):
        # only interesting folders contain lossless music
        if extension not in [os.path.splitext(fname)[1] for fname in filenames]:
            continue
        # has to have a modtime newer than start_time
        if os.path.getmtime(dirpath) < start_time:
            continue
        sys.stdout.write(dirpath + '\n')
        if new_location:
            # figure out a 'better' name
            fullname = os.path.sep.join(dirpath.split(os.path.sep)[-2:])
            fullname = fullname.replace(os.path.sep, '__')
            fullname = TROUBLESOME_FILENAME_CHARS.sub('_', fullname)
            newpath = os.path.normpath(os.path.join(new_location, fullname))
            # now copy to that folder
            sys.stdout.write("  => " + newpath + "\n")
            if os.path.isdir(newpath):
                sys.stdout.write("  " + newpath + " already exists; overwriting...\n")
                shutil.rmtree(newpath)
            shutil.copytree(dirpath, newpath)


if __name__ == "__main__":
    main(sys.argv)
