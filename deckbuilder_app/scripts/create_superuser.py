from deckbuilder_app.models import User

User.objects.create_superuser('martin', 'martinnoya@gmail.com', 'admin')