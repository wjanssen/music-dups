import sys, os

for dirpath, dirnames, filenames in os.walk(sys.argv[1]):
    for filename in filenames:
        basename, ext = os.path.splitext(filename)
        if ext == ".m4a" and (basename + ".flac") not in filenames:
            print os.path.join(dirpath, filename)
        elif ext == ".m4a":
            os.unlink(os.path.join(dirpath, filename))
