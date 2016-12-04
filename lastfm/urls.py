from django.conf.urls import include, url
from django.contrib import admin
from views import *

urlpatterns = [
    url(r'^connect/', lastfm_connect, name='lastfm_connect'),
    url(r'^unlink/', lastfm_unlink, name='lastfm_unlink'),
    url(r'^callback/', lastfm_callback, name='lastfm_callback'),
    url(r'^annual_summary/', lastfm_annual_summary, name='lastfm_annual_summary'),
    url(r'^synchronise/(?P<period>\S+)/', lastfm_synchronise, name='lastfm_synchronise'),
]
