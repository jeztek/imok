import re, random, hashlib, pytz
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

from timeutils import *

#TZ_CHOICES = pytz.common_timezones
TZ_CHOICES = (('US/Pacific', 'US/Pacific'), ('US/Eastern', 'US/Eastern'))

class UserProfile(models.Model):
    user         = models.ForeignKey(User, unique=True)
    userKey      = models.CharField(max_length=5)
    phoneNumber	 = models.CharField(max_length=40)
    tz           = models.CharField(max_length=50, \
                                    choices=TZ_CHOICES, \
                                    default="US/Pacific", \
                                    verbose_name="Time zone")

    def __unicode__(self):
        return self.user.username + " - " + self.phoneNumber


class RegisteredEmail(models.Model):
    hashKey      = models.CharField(max_length=50, unique=True, db_index=True)
    user         = models.ForeignKey(User)
    email        = models.EmailField()
    isBlocked    = models.BooleanField(default=False)

    @classmethod
    def generateHashKey(cls, email):
        return hashlib.sha1(self.email).hexdigest()
        
    def permalink(self, host=''):
        return "%s/unsubscribe?id=%s" % (host, self.hashkey)
    
    
class Post(models.Model):
    user		    = models.ForeignKey(User)
    datetime	 = models.DateTimeField()

    latitude	 = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    message		 = models.CharField(max_length=140)
    position  = models.CharField(max_length=140)
    isOk      = models.BooleanField(default=True)

    postId    = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.user.username + " - " + self.message

    @classmethod
    def generatePostId(cls):
        return str('%016x' % random.getrandbits(64))

    @classmethod
    def findTags(cls, text):
        hash_regex = re.compile(r'(#\S+)(?:\s?)([^#]*)(?=#?)')
        return hash_regex.findall(text)

    def tags(self):
        return Post.findTags(self.message)

    def hasLocation(self):
        return not (self.latitude == None or self.longitude == None)

    @classmethod
    def fromText(cls, text):
        post = Post(message=text)
        tags = Post.findTags(text)
        isOk = false
        atText = ''
        for tup in tags:
            if tup[0] == '#imok': ok = True
            if tup[0] == '#loc':  continue

            ll_regex = re.compile(r'\s*(-?\d+\.\d+),(-?\d+\.\d+)')
            m = ll_regex.match(tup[1])
            if m:
                post.latitude = float(m.group(1))
                post.longitude = float(m.group(2))
            else:
                atText += tup[1] + ' '
        post.positionText = atText
        post.isOk = isOk
        return post

    def permalink(self, host=''):
        return '%s/message?postId=%s' % (host, self.postId)

