from fabric.api import env, run, task

env.user = "ec2-user"
env.key_filename = ["./templatekey.pem"]

# server setup,
# easy_install virtualenv and activate ENV
# sudo yum install -y mysql python-mysql python-imaging
# pip install flask, etc
# configure apache, install db

