from django.utils import simplejson
from django.http import HttpResponse

# Return plain text response
def TextResponse(text):
	return HttpResponse(text, mimetype="text/plain; charset=\"utf-8\"")


# Return JSON encoded representation of object as text response
def JsonResponse(obj):
	return HttpResponse(simplejson.dumps(obj, ensure_ascii=False),
		mimetype="text/plain; charset=\"utf-8\"")

