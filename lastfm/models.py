from django.db import models
from django.contrib.auth.models import User

class LastfmUser(models.Model):
	user = models.ForeignKey(User)
	username = models.CharField(max_length=255)
