from django.conf.urls.defaults import *

urlpatterns = patterns('app.views',
	(r'^$', 'home'),
	(r'^user/login/$', 'user_login'),
	(r'^user/logout/$', 'user_logout'),
	(r'^user/register/$', 'user_register'),

	(r'^search/$', 'search'),

	(r'^user/register/phone/$', 'user_register_phone'),
	(r'^user/register/phone/delete/(?P<user_key>\w+)/$', 'user_register_phone_delete'),

	(r'^user/register/twitter/$', 'user_register_twitter'),
	(r'^user/register/twitter/delete/$', 'user_register_twitter_delete'),
					   
	(r'^user/register/facebook/$', 'user_register_facebook'),

	(r'^data/register/(?P<user_key>\w+)/$', 'data_register'),
	(r'^data/imok/(?P<user_key>\w+)/$', 'data_imok'),
)
