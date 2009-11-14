import os, sys

# WSGI apps should not output anything to stdout, we redirect here
sys.stdout = sys.stderr

sys.path.append(os.path.realpath(os.path.dirname(__file__)) + '/..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'done.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
