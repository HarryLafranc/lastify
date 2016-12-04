from fabric.api import env, run, cd, hosts, abort, prompt
from fabric.contrib.console import confirm
from fabric.colors import red, blue, green, magenta, yellow

#env.always_use_pty=False

uwsgi = ('root@151.80.42.152')

repo = "/home/lastify/lastify/"

print red("**********************")
print red("\tUsage : \n")
print green(" Update du serveur de prod : ")
print blue("fab update_uwsgi:'v1.3.3.7'")
print green(" Update des requirements : ")
print blue("fab update_requirements")
print green(" Start du serveur : ")
print blue("fab uwsgi_start")
print green(" Stop du serveur : ")
print blue("fab uwsgi_stop")
print red("\n**********************")

def uwsgi_stop():
    """Restart uwsgi worker"""
    run("supervisorctl stop lastify")

def uwsgi_start():
    """Restart uwsgi worker"""
    run("supervisorctl start lastify")

def git_pull(tag=None):
    if tag is None:
        run("su - lastify -c \"cd "+repo+" && git pull origin master\"")
    else:
        run("su - lastify -c \"cd "+repo+" && git fetch && git checkout " + tag+"\"")

@hosts(uwsgi)
def update_requirements():
    run("su - lastify -c \"cd "+repo+" && pip install -r requirements_prod.txt\"")

@hosts(uwsgi)
def update_uwsgi(tag):
    uwsgi_stop()
    git_pull(tag)
    uwsgi_start()
