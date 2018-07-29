#!/usr/bin/env python
#
# Copy newly ripped music from iTunes artist/folder to somewhere else
#

import sys, os, os.path, time, shutil, re
from collections import defaultdict


TROUBLESOME_FILENAME_CHARS = re.compile(r'[^-\._0-9A-Za-z]')


def usage(msg=None):
    if msg:
        sys.stderr.write(msg + "\n")
    sys.stderr.write("Usage: python %s <root-directory> <age-in-days> [NEW-LOCATION=<dir> (default: None)] [EXTENSION=<file-extension> (default: m4a)]\n" % (sys.argv[0],))
    sys.exit(1)

def decode_track_and_disk (filenames):
    # iTunes track names start with either %02i, or %i-%02i, depending
    # on whether the track names are there.
    tracks = defaultdict(list)
    for filename in filenames:
        firstpart = filename.split()[0]
        m = re.match(r"([0-9]+)-([0-9]+)", firstpart)
        if m:
            tracks[int(m.group(1))].append((int(m.group(2)), filename))
        else:
            m = re.match(r"([0-9]+)", firstpart)
            if m:
                tracks[1].append((int(m.group(1)), filename))
            else:
                sys.stderr.write("Invalid disk/track # '" + firstpart + "' in '" + filename + "\n")
                raise RuntimeError("Invalid track #")
    return tracks

def removehashes(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if '#' in filename:
                oldname = os.path.join(dirpath, filename)
                newname = os.path.join(dirpath, re.sub('#', 'No. ', filename))
                sys.stdout.write("  " + oldname + "\n     => " + newname + "\n")
                os.rename(oldname, newname)

def removemp3s(directory):
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if os.path.splitext(filename)[1] == ".mp3":
                name = os.path.join(dirpath, filename)
                sys.stdout.write("  removing " + name + "...\n")
                os.unlink(name)

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
        # check to see if we have all tracks.  Not quite effective,
        # as it will miss tracks at the end (if they're missing)
        tracks = decode_track_and_disk([f for f in filenames if f.endswith(extension)])
        for disk, trackinfo in tracks.items():
            tracknumbers = [x[0] for x in trackinfo]
            if len(tracknumbers) != max(tracknumbers):
                sys.stdout.write("*** Missing tracks: " + dirpath + " disk " + str(disk) + \
                                 "; only have " + ", ".join([str(t) for t in tracknumbers]) + "\n")
                continue
        # Now move to a new location if specified
        if new_location:
            # figure out a 'better' name
            fullname = os.path.sep.join(dirpath.split(os.path.sep)[-2:])
            fullname = fullname.replace(os.path.sep, '__')
            fullname = TROUBLESOME_FILENAME_CHARS.sub('_', fullname)
            newpath = os.path.normpath(os.path.join(new_location, fullname))
            # now copy to that folder
            # split multiple disks
            for disk, trackinfo in tracks.items():
                if len(tracks) > 1:
                    # add disk # to file path
                    diskified_newpath = newpath + "_disk_" + str(disk)
                else:
                    diskified_newpath = newpath
                if os.path.isdir(diskified_newpath):
                    sys.stdout.write("  " + diskified_newpath + " already exists; overwriting...\n")
                    shutil.rmtree(diskified_newpath)
                os.mkdir(diskified_newpath)
                sys.stdout.write("  => " + diskified_newpath + "\n")
                for (trackno, trackfile) in trackinfo:
                    newfilename = "%02d %s" % (trackno, ' '.join(trackfile.split(' ')[1:]))
                    shutil.copyfile(os.path.join(dirpath, trackfile),
                                    os.path.join(diskified_newpath, newfilename))
                sys.stdout.write("Removing # characters...\n")
                removehashes(diskified_newpath)
                sys.stdout.write("Removing mp3 files...\n")
                removemp3s(diskified_newpath)


if __name__ == "__main__":
    main(sys.argv)
