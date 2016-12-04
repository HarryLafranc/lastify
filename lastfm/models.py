from django.db import models
from django.contrib.auth.models import User

class LastfmUser(models.Model):
	user = models.ForeignKey(User)
	username = models.CharField(max_length=255)

	def __unicode__(self):
		return "%s - %s" % (self.username, self.user)
