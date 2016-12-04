from django.db import models
from django.contrib.auth.models import User

class SpotifyUser(models.Model):
	user = models.ForeignKey(User)
	username = models.CharField(max_length=255, blank=True)
	token = models.CharField(max_length=255, blank=True)
	refresh_token = models.CharField(max_length=255, blank=True)
