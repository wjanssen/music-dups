import sys, os, re

for dirpath, dirnames, filenames in os.walk(sys.argv[1]):
    for filename in filenames:
        if '#' in filename:
            os.rename(os.path.join(dirpath, filename), os.path.join(dirpath, re.sub('#', 'No. ', filename)))
