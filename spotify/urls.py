from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^connect/', views.spotify_connect, name='spotify_connect'),
    url(r'^callback/', views.spotify_callback, name='spotify_callback'),
    url(r'^unlink/', views.spotify_unlink, name='spotify_unlink'),
]
