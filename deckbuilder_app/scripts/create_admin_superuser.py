from decouple import config
from django.db import IntegrityError

from deckbuilder_app.models import User


def create_admin_superuser():
    username = config('ADMIN_USERNAME')
    email = config('ADMIN_EMAIL')
    password = config('ADMIN_PASSWORD')

    try:
        User.objects.create_superuser(username, email, password)
        print("Created superuser")
    except IntegrityError:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.email = email
        user.save()
        print("Updated superuser")
