import os, tempfile
import MySQLdb
from datetime import datetime

from config import db

global_registry = {}
filter_registry = {}

class Image(object):
    """Wrapper for database rows from images table."""

    @staticmethod
    def image_location(parent_id, id):
        if parent_id:
            loc = '/static/uploads/%s' % parent_id
        else:
            loc = '/static/uploads/%s' % id
        return loc

    def absolute_url(self):
        directory = Image.image_location(self.parent_id, self.id)
        return os.path.join(directory, self.image)

    def get_relative_path(self):
        return "." + self.absolute_url()

    def __getattr__(self, attribute):
        """Map attribute requests to keys of row instance."""
        if attribute in self.keys:
            return self.row[attribute]
        else:
            raise AttributeError("%r has no attribute %r" % (self.row,
                                                             attribute))
    def __init__(self, sqlite_row):
        self.row = sqlite_row
        self.keys = sqlite_row.keys()


def filter(f):
    """ Use as decorator to mark template filter functions."""
    filter_registry[f.func_name] = f
    return f

def globalfuncs(f):
    """ Use as decorator to mark template global functions."""
    global_registry[f.func_name] = f
    return f

def get_db(dict_cursor=True):
    mysqldb = db.get_db()
    # if not in a request we won't be connected
    if not mysqldb:
        mysqldb = db.connect()
    # return a DictCursor
    if dict_cursor:
        return mysqldb.cursor(MySQLdb.cursors.DictCursor)
    else:
        return mysqldb.cursor()

def config_templates(app):
    # add custom template filters
    for name, func in filter_registry.items():
        app.jinja_env.filters[name] = func
    # and global template functions
    for name, func in global_registry.items():
        app.jinja_env.globals[name] = func
    
@filter
def image_path(image):
    if not isinstance(image, Image):
        image = Image(image)
    loc = image.absolute_url()
    return loc

@globalfuncs
def num_images():
    db = get_db(False)
    db.execute('select count(*) from instaclone_images')
    total_count = db.fetchone()[0]
    return total_count

@globalfuncs
def top_images():
    sql = """SELECT count(*) as cnt,
                    instaclone_images.id,
                    instaclone_images.parent_id,
                    instaclone_images.image,
                    instaclone_images.name
             FROM instaclone_likes
                INNER JOIN instaclone_images
                ON instaclone_likes.image = instaclone_images.id
             GROUP BY instaclone_images.id
             ORDER BY cnt DESC limit 5;"""
    db = get_db()
    db.execute(sql)
    rows = db.fetchall()
    return rows

@filter
def likes(num):
    if num < 10:
        return "Less than 10"
    else:
        num = num / 10 * 10 # cheating by using integer div
        return "%s+" % num
    
@filter
def naturaldate(dt):
    # image.dt may be string like 2013-02-06 20:18:29
    # apparently pysqlite3 doesn't return datetime objects
    if isinstance(dt, (str, unicode)):
       dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()
    print now
    print dt
    diff = now - dt
    print diff
    if diff.days > 30:
        return "about %s months ago" % (diff.days / 30)
    elif diff.days > 0:
        return "about %s days ago" % diff.days
    elif diff.seconds > (60 * 60):
        return "about %s hours ago" % (diff.seconds / 60 * 60)
    else:
        return "about %s minutes ago" % (diff.seconds / 60)

def new_filename(filename):
    """Given a path to a file returns a new filename in the same
    directory with a .jpg extension and a unique filename."""

    directory = os.path.dirname(filename)
    (fd, fn) = tempfile.mkstemp(suffix=".jpg",
                                prefix='filter',
                                dir=directory)
    # Close the unix file descriptor returned by mkstemp
    os.close(fd)
    return fn

def insert_image(image, name, parent=None, mv=True):
    """Insert an image from form upload into the db and move into
    position on the filesystem."""

    try:
        # Might be file form object
        filename = image.filename
    except:
        # might just be string filename
        filename = image
    # use filename as name for image if not otherwise supplied
    if not name:
        name = filename
    db = get_db()
    db.execute("""insert into
                              instaclone_images(parent_id, image, name)
                                  values(%s, %s, %s)""",
                          [parent, filename, name])
    pk = db.lastrowid
    # If handling a file upload will need to move from /tmp location
    if mv:
        directory = "." + Image.image_location(pk, parent)
        # make parent directory if necessary
        if not os.path.isdir(directory):
            os.mkdir(directory)
        image.save('%s/%s' % (directory, image.filename))
    return pk

