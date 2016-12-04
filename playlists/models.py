from django.db import models
from django.contrib.auth.models import User

class Playlist(models.Model):
	spotify_url = models.CharField(max_length=255)
	lastfm_url = models.CharField(max_length=255)
	user = models.ForeignKey(User) 