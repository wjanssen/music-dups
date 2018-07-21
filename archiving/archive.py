#!/usr/bin/env python

"""
Create tar.bz2 files for a collection of albums, one per album.
Assumes music is stored as ARTIST/ALBUM/SONG in MP3 files.
Arguments are names of directories where the music files are stored.
Tar file is left in ARTIST/ALBUM/ directory.
Disk and track numbers are trimmed off -- they should be in the ID3 metadata.

The command-line arguments to this script are one or more "roots", which
are the directories where the ARTIST directories are stored.

A file /tmp/rmfile is also created, containing the names of song files which
have been copied to archives.  This may optionally be used to remove the
song files.
"""

import sys, os, re, collections, tarfile

roots = sys.argv[1:]

found = collections.defaultdict(list)      # map triple of (artist, album, song) to [filepath...]

trackno = re.compile(r'^(?P<disk>\(.+?\)\s+)?(?P<track>[0-9]+)?(?P<sep>\s*-\s*[0-9]*)?\s+')

rmfile = open("/tmp/rmfile", "w")

for index, root in enumerate(roots):
    count = 0
    for dirpath, dirs, files in os.walk(root):
        albumdir = None
        artistdir = None
        for filename in files:
            if filename.startswith("."):        # ignore dotfiles
                continue
            basename, ext = os.path.splitext(filename)
            if ext == ".mp3":
                songname = basename
                if trackno.match(songname):
                    songname = trackno.sub('', songname)
                albumdir = os.path.basename(dirpath)
                artistdir = os.path.basename(os.path.dirname(dirpath))
                key = (artistdir, albumdir, songname, dirpath)
                value = os.path.join(dirpath, filename)
                found[key].append((index, value))
                count += 1
    artists = sorted(set([x[0] for x in found]))
    albums = sorted(set([x[:2] for x in found]))

    # re-do everything by artist/album
    by_artist_album = collections.defaultdict(dict)
    for artist, album in albums:
        for key in found:
            if key[0] == artist and key[1] == album:
                by_artist_album[(artist, album)][key[2]] = found[key]

    for (artist, album), songs in by_artist_album.items():
        # figure the albumdir
        albumdir = os.path.dirname(songs[songs.keys()[0]][0][1])
        archive_path = os.path.join(albumdir, '@'.join([re.sub('[^-A-Za-z0-9_]', '_', artist), re.sub('[^-A-Za-z0-9_]', '_', album)]) + ".tar.bz2")
        tarfile = tarfile.open(archive_path, mode='w:bz2')
        for songname, locations in songs.items():
            for idx, location in locations:
                tarfile.add(location, arcname=songname+".mp3")
                rmfile.write("%s\n" % (location,))
        tarfile.close()
        print archive_path
