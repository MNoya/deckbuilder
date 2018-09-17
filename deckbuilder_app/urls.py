from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views

from deckbuilder_app.views import decks as deck_views
from deckbuilder_app.views import users as user_views
from deckbuilder_app.views import galaxy as galaxy_views

urlpatterns = \
    [
        path('', deck_views.index, name='index'),
        path('decks/', deck_views.DeckListView.as_view(), name='deck_list'),
        path('decks/<int:pk>/', deck_views.DeckDetailView.as_view(), name='deck_detail'),
        path('decks/<int:pk>/edit/', deck_views.deck_edit, name='deck_edit'),

        path('deckbuilder/', deck_views.new_deck, name='new_deck'),

        path('galaxy/', galaxy_views.galaxy_map_list, name='galaxy'),
        path('galaxy/<int:pk>', galaxy_views.GalaxyDetailView.as_view(), name='galaxy_detail'),

        path('cards/<int:pk>', deck_views.CardDetailView.as_view(), name='card_detail'),

        ## User Management ##
        path('login/', auth_views.LoginView.as_view(template_name='views/login.html'), name='login'),
        path('logout/', auth_views.LogoutView.as_view(template_name='views/logout.html'), name='logout'),

        path('register/', user_views.register, name='register'),
        path('validate/<token>/', user_views.validate_email, name='validate_email_token'),

        path('recover-password/', user_views.recover_password, name='recover_password'),
        path('reset-password/', user_views.reset_password, name='reset_password_post'),
        path('reset-password/<token>/', user_views.reset_password, name='reset_password_get'),

        # url(r'^profile/$', views.my_profile, name='my_profile'),
        # url(r'^profile/(?P<pk>[0-9]+)/$', views.user_profile, name='user_profile'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
