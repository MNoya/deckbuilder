#!/usr/bin/env bash
git -C ~/deckbuilder reset --hard HEAD
git -C ~/deckbuilder/ pull
source ~/venvs/deckbuilder/bin/activate
pip install -r ~/deckbuilder/requirements.txt
python ~/deckbuilder/manage.py migrate
python ~/deckbuilder/manage.py collectstatic --noinput
sudo /etc/init.d/nginx restart
uwsgi --reload /tmp/project-master.pid