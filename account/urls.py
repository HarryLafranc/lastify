# -*- coding: utf-8 -*-
from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^login/$', views.login, name='account_login'),
    url(r'^logout/', views.logout, name='account_logout'),
    #url(r'^register/', views.register, name='account_register'),
    url(r'^settings/', views.settings, name='account_settings'),
]
