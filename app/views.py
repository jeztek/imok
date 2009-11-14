from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist

from helpers import JsonResponse


def home(request):
    return render_to_response('home.html', { })


def data_post(request):
	try:
		uuid	= request.REQUEST['uuid']
		name	= request.REQUEST['name']
		lat		= request.REQUEST['lat']
		lon		= request.REQUEST['lon']

	except KeyError:
		return JsonResponse({'error' : 'missing parameter'})

	timestamp = datetime.today()

	return JsonResponse({'result' : True})


