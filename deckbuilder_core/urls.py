"""deckbuilder_core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from deckbuilder_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('decks/', include('deckbuilder_app.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='views/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='views/logout.html'), name='logout'),
    path('register/', views.register, name='register'),

    # url(r'^profile/$', views.my_profile, name='my_profile'),
    # url(r'^profile/(?P<pk>[0-9]+)/$', views.user_profile, name='user_profile'),
    #
    path('validate/<token>/', views.validate_email, name='validate_email_token'),

    path('recover-password/', views.recover_password, name='recover_password'),
    path('reset-password/', views.reset_password, name='reset_password_post'),
    path('reset-password/<token>/', views.reset_password, name='reset_password_get'),

]
