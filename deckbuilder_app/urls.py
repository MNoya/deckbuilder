from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = \
    [
        path('login/', auth_views.LoginView.as_view(template_name='views/login.html'), name='login'),
        path('logout/', auth_views.LogoutView.as_view(), name='logout'),
        path('register/', views.register, name='register'),
        # url(r'^profile/$', views.my_profile, name='my_profile'),
        # url(r'^profile/(?P<pk>[0-9]+)/$', views.user_profile, name='user_profile'),
        #
        # url(r'^(?P<token>[0-9a-f-]+)/$', views.validate_email, name='validate_email_token'),
        # url(r'reset_password/$', views.reset_password, name='reset_password_post'),
        # url(r'reset_password/(?P<token>[0-9a-f-]+)/$', views.reset_password, name='reset_password_get'),

        path('', views.DeckListView.as_view(), name='deck_list'),
        path('<int:pk>/', views.DeckDetailView.as_view(), name='deck_detail'),
        path('<int:pk>/edit/', views.deck_edit, name='deck_edit'),
        path('new/', views.new_deck, name='new_deck'),
        path('cards/<int:pk>', views.CardDetailView.as_view(), name='card_detail'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
