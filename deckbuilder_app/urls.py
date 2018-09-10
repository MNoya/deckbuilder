from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views

urlpatterns = \
    [
        path('', views.DeckListView.as_view(), name='deck_list'),
        path('<int:pk>/', views.DeckDetailView.as_view(), name='deck_detail'),
        path('<int:pk>/edit/', views.deck_edit, name='deck_edit'),
        path('new/', views.new_deck, name='new_deck'),
        path('cards/<int:pk>', views.CardDetailView.as_view(), name='card_detail'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
