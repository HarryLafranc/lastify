from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^connect/', views.lastfm_connect, name='lastfm_connect'),
    url(r'^unlink/', views.lastfm_unlink, name='lastfm_unlink'),
    url(r'^callback/', views.lastfm_callback, name='lastfm_callback'),
    url(r'^annual_summary/', views.lastfm_annual_summary, name='lastfm_annual_summary'),
    url(r'^synchronise/(?P<period>\S+)/', views.lastfm_synchronise, name='lastfm_synchronise'),
]
