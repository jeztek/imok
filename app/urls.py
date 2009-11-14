from django.conf.urls.defaults import *

urlpatterns = patterns('app.views',
	(r'^$', 'home'),
	(r'^user/login/$', 'user_login'),
	(r'^user/register/$', 'user_register'),
	(r'^user/register/twitter/$', 'user_register_twitter'),

	(r'^data/post/$', 'data_post'),
)
