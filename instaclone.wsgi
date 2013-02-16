activate_this = '/home/ec2-user/ENV/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

from webapplicaiton import app as application

