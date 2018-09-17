# Generated by Django 2.1 on 2018-08-22 19:44

import deckbuilder_app.common
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('avatar', models.ImageField(default='default/profile_image.jpg', upload_to='avatars')),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True)),
                ('is_active', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('cost', models.PositiveSmallIntegerField()),
                ('rarity', models.IntegerField(choices=[(0, "Newbie's"), (1, 'Common'), (2, 'Rare'), (3, 'Epic'), (4, 'Legendary')], default="Newbie's")),
                ('card_type', models.IntegerField(choices=[(0, 'Unit'), (1, 'Spell')], default='Unit')),
                ('race', models.IntegerField(choices=[(0, 'Quadruple Radiance Empire'), (1, 'Roughrock Weald'), (2, 'Zen Valley'), (3, 'Inferno'), (4, "Deus of Winter's Apostle"), (5, 'Recluse'), (6, 'Paradise Harbor')], default='Quadruple Radiance Empire')),
                ('attack', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('defense', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('art', models.ImageField(blank=True, null=True, upload_to='')),
            ],
            options={
                'db_table': 'card',
                'ordering': ['cost', '-rarity', '-race', '-card_type', 'name'],
            },
        ),
        migrations.CreateModel(
            name='CardInDeck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('copies', models.PositiveIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(3), django.core.validators.MinValueValidator(1)])),
                ('card', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deckbuilder_app.Card')),
            ],
            options={
                'db_table': 'card_in_deck',
                'ordering': ['card__cost', '-card__rarity', '-card__race', '-card__card_type', 'card__name']
            },
        ),
        migrations.CreateModel(
            name='Deck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('time_created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('cards', models.ManyToManyField(through='deckbuilder_app.CardInDeck', to='deckbuilder_app.Card')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'deck',
            },
        ),
        migrations.CreateModel(
            name='EmailToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('expiry_date', models.DateTimeField(default=deckbuilder_app.common.default_expiration_delta, editable=False)),
                ('email', models.EmailField(max_length=254)),
                ('user', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='email_token', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResetPasswordToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('expiry_date', models.DateTimeField(default=deckbuilder_app.common.default_expiration_delta, editable=False)),
                ('user', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='reset_password_token', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='cardindeck',
            name='deck',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='deckbuilder_app.Deck'),
        ),
        migrations.AlterUniqueTogether(
            name='card',
            unique_together={('name', 'race', 'rarity')},
        ),
        migrations.AlterUniqueTogether(
            name='cardindeck',
            unique_together={('card', 'deck')},
        ),
    ]
