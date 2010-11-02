from django.conf.urls.defaults import *

urlpatterns = patterns('app.views',
    (r'^$', 'intro'),
    (r'about/$', 'about'),
    (r'getInvolved/$', 'getInvolved'),
    (r'message/$', 'message'),
    (r'unsubscribe/$', 'unsubscribe'),

    (r'login/$', 'login'),
    (r'logout/$', 'logout'),
    (r'signup/$', 'signup'),
                       
    (r'home/$', 'home'),
    (r'email/$', 'email'),
    (r'email/remove/$', 'emailRemove'),
    (r'profile/edit/$', 'profileEdit'),
    (r'profile/delete/$', 'profileDelete'),
    (r'profile/deleted/$', 'profileDeleted'),
    (r'download/$', 'download'),
)
