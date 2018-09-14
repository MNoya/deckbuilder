git -C ~/deckbuilder reset --hard HEAD
git -C ~/deckbuilder/ pull
source ~/venvs/deckbuilder/bin/activate
python ~/deckbuilder/manage.py migrate
python ~/deckbuilder/manage.py collectstatic --noinput
sudo /etc/init.d/nginx restart