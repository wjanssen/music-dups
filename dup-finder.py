#!/usr/bin/env python

"""
Find duplicate songs in a collection of music stored as
ARTIST/ALBUM/SONG MP3 files.  Trims off disk and track numbers, which
should be in the ID3 tag for the file.  Reports on duplicate songs
(which may be alternate takes).  The argument or arguments are root
directories to scan the subtree of.

If multiple roots are specified, will create a bash script in /tmp/movefile
which attempts to copy everything to the first root specified, but does not
execute said script.

If only one root is specified, just does duplicate analysis, but
will generate a file /tmp/rmfile containing the names of songs which
it thinks are duplicates.

Everything is done by matching names and titles; no inspection of the MP3 file
or its metadata is performed.
"""

import sys, os, re, collections

roots = sys.argv[1:]

found = collections.defaultdict(list)      # map triple of (artist, album, song) to [filepath...]

trackno = re.compile(r'^(?P<disk>\(.+?\)\s+)?(?P<track>[0-9]+)?(?P<sep>\s*-\s*[0-9]*)?\s+')

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
                songname = re.sub(r'\?$', '_', songname)
                songname = songname.strip('"')
                albumdir = os.path.basename(dirpath)
                artistdir = os.path.basename(os.path.dirname(dirpath))
                key = (artistdir, albumdir, songname)
                value = os.path.join(dirpath, filename)
                found[key].append((index, value))
                count += 1

    print 'finished', root, 'with', count, 'songs found'
print 'total found:', len(found)
artists = sorted(set([x[0] for x in found]))
albums = sorted(set([x[:2] for x in found]))

# re-do everything by artist/album
by_artist_album = collections.defaultdict(dict)
for artist, album in albums:
    for key in found:
        if key[0] == artist and key[1] == album:
            by_artist_album[(artist, album)][key[2]] = found[key]

del found

for (artist, album), songs in by_artist_album.items():
    print artist, ' / ', album
    for song in songs:
        sys.stdout.write("    %-60s %s\n" % (song, ', '.join([str(x[0]) for x in songs[song]])))

if len(roots) > 1:
    movefile = open("/tmp/movefile", "w")
    for (artist, album), songs in by_artist_album.items():
        todir = os.path.join(roots[0], artist, album)
        if not os.path.exists(todir):
            movefile.write('mkdir -p "%s"\n' % (re.sub('"', '\\"', todir),))
        for songname, locations in songs.items():
            if 0 not in [x[0] for x in locations]:
                # copy it to root 0
                songfilepath = locations[0][1]
                fromfile = re.sub('"', '\\"', songfilepath)
                songfilename = songname + ".mp3"
                tofile = re.sub('"', '\\"', os.path.join(todir, songfilename))
                movefile.write('echo "%s / %s / %s"\n' % (artist, album, songname))
                movefile.write('cp "%s" "%s"\n' % (fromfile, tofile))
else:

    def clean_filename(location):
        basename = os.path.basename(location)
        return trackno.match(basename) is None

    # looking for dups in the single root
    rmfile = open("/tmp/rmfile", "w")
    if not os.path.exists('/home/wjanssen/music-backup'):
        os.makedirs('/home/wjanssen/music-backup')
    for (artist, album), songs in by_artist_album.items():
        albumdir = os.path.join(roots[0], artist, album)
        for songname, locations in songs.items():
            if len(locations) > 1:
                print artist, '/', album, '/', songname
                clean = [location for idx, location in locations if clean_filename(location)]
                unclean = [location for idx, location in locations if not clean_filename(location)]
                for idx, location in locations:
                    print '        ', location, '*' if location in clean else ' '
                if len(clean) > 0 and len(unclean) > 0:
                    print '         (suggest remove ' + ', '.join(unclean)
                    for filename in unclean:
                        rmfile.write(filename + '\n')
                elif len(clean) == 0:
                    print '*****'
                    print ''
                    print 'Only unclean versions of', artist, '/', album, '/', songname, 'found.'
                    for filename in unclean:
                        print '          ', filename
                    print ''
                    print '*****'
                elif len(unclean) == 0:
                    print '*****'
                    print ''
                    print 'Multiple clean versions of', artist, '/', album, '/', songname, 'found!'
                    for filename in clean:
                        print '          ', filename
                    print ''
                    print '*****'
