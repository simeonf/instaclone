activate_this = '/var/www/instaclone/ENV/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from instaclone.webapp import app as application
