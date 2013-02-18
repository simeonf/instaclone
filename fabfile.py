from fabric.api import env, run, sudo, task, cd, hide

env.user = "ec2-user"
env.key_filename = ["~/.ssh/templatekey.pem"]

@task
def yum():
    with hide('output'):
        sudo("yum install -y mysql mysql-server")
        sudo("yum install -y MySQL-python python-imaging")
        sudo("yum install -y httpd mod_wsgi")
        sudo("yum install -y git")
    sudo("/etc/init.d/mysqld start")
    sudo("/etc/init.d/httpd start")

@task
def clear_app_dir():
    sudo('rm -rf /var/www/instaclone')

@task
def populate_db():
    with cd('/var/www/instaclone/instaclone'):
        run('/var/www/instaclone/ENV/bin/python populate_db.py ./sample-images/')
    
@task
def setup_app():
    sudo('mkdir /var/www/instaclone')
    sudo('chown ec2-user:ec2-user /var/www/instaclone')
    sudo('easy_install virtualenv')
    with cd('/var/www/instaclone'):
        run('virtualenv --system-site-packages ENV')
        with hide('output'):
            run('ENV/bin/pip install flask flask-mysql')
            run('git clone git://github.com/simeonf/instaclone.git')
        #run('mkdir instaclone/static/uploads')
        run('ln -s /var/www/instaclone/instaclone ENV/lib/python2.6/site-packages/')
        # setup apache
        response = sudo('ls /etc/httpd/conf/httpd.conf.old', quiet=True)
        if response.return_code > 0: # ls failed
            sudo("cp /etc/httpd/conf/httpd.conf /etc/httpd/conf/httpd.conf.old")
        sudo("cp /etc/httpd/conf/httpd.conf.old httpd.conf")
        sudo("cat instaclone/instaclone.conf >> httpd.conf")
        sudo("cp httpd.conf /etc/httpd/conf/httpd.conf")
        sudo("/etc/init.d/httpd restart")
        # setup mysql
        run("mysql -u root < instaclone/schema.mysql")

@task
def setup():
    yum()
    setup_app()
    populate_db()
