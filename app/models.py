from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

class PhoneUser(models.Model):
	user            = models.ForeignKey(User)
	user_key        = models.CharField(max_length=5)
	phone_number	= models.CharField(max_length=40)
	is_valid		= models.BooleanField()
	
	def __unicode__(self):
		return self.user.username + " - " + self.phone_number


class TwitterUser(models.Model):
	user		= models.ForeignKey(User)
	username	= models.CharField(max_length=40)
	password	= models.CharField(max_length=140)
	
	def __unicode__(self):
		return self.user.username + " - " + self.username


class Post(models.Model):
	user		= models.ForeignKey(User)
	datetime	= models.DateTimeField()

	lat			= models.FloatField()
	lon			= models.FloatField()
	message		= models.CharField(max_length=40)

	def __unicode__(self):
		return self.user.username + " - " + self.message
