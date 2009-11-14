from django.conf.urls.defaults import *

urlpatterns = patterns('app.views',
	(r'^$', 'home'),
	(r'^user/login/$', 'user_login'),
	(r'^user/register/$', 'user_register'),
        (r'^user/register/phone/$', 'user_register_phone'),
	(r'^user/register/twitter/$', 'user_register_twitter'),
	(r'^user/register/facebook/$', 'user_register_facebook'),

	(r'^data/post/$', 'data_post'),
)
