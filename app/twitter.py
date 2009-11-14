import tweepy

from django.core.exceptions import ObjectDoesNotExist

from models import TwitterUser


def twitter_post(user, message):
	try:
		tuser = TwitterUser.objects.get(user=user)
	except ObjectDoesNotExist:
		return False
	
	basic_auth = tweepy.BasicAuthHandler(tuser.username, tuser.password)

	api = tweepy.API(basic_auth)
	update = api.update_status(message)
	print update.text
	return True


