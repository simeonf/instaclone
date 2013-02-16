from glob import glob
from shutil import copyfile
import os, tempfile, random

from util import insert_image, get_db

class Image(object):
    """Class to fake flask file upload object. Use in bulk importer
    only."""
    
    def __init__(self, full_path):
        self.filename = os.path.basename(full_path)
        self.full_path = full_path
        
    def save(self, dest):
        copyfile(self.full_path, dest)
    
    
def main(loc, opt):
    files = glob(os.path.join(loc, "*jpg"))
    d = tempfile.mkdtemp()
    # copy all files in loc to /tmp directory
    for f in files:
        dest = os.path.join(d, os.path.basename(f))
        copyfile(f, dest)
        if opt.verbose:
            print "Copying %s" % f
    files = glob(os.path.join(d, "*jpg"))
    db = get_db()
    for f in files:
        im = Image(f)
        if opt.verbose:
            print "Inserting into the database %s" % im.filename
        pk = insert_image(im, im.filename.replace("-", " "),
                          None, True)
        for i in xrange(random.randint(0, 100)):
            curs = db.execute("""insert into instaclone_likes(image)
                             values(%s)""", [pk])

if __name__ == '__main__':
    from optparse import OptionParser
    p = OptionParser(usage="python populate_db.py ./sample-images")
    p.add_option("-v", "--verbose", action="store_true",
                 help="Add -v to see debug output")
    opts, args = p.parse_args()
    if not (len(args) == 1 and os.path.isdir(args[0])):
        raise Exception("Please specify a path to a directory.")
    main(args[0], opts)


