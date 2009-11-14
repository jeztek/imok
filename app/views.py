from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
from django.contrib.auth.decorators import login_required

from core.helpers import JsonResponse
from models import User, UserProfile, TwitterUser, Post
from twitter import twitter_post


def home(request):
    return render_to_response('home.html', {})


def user_login(request):
	if request.method == 'POST':
		try:
			username = request.REQUEST['u']
			password = request.REQUEST['p']
		except KeyError:
			return render_to_response('home.html', {
				'message' : 'invalid username or password'
			})

		user = auth.authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				auth.login(request, user)
				return render_to_response('home.html', {
					'message' : 'login successful',
				})

		return render_to_response('home.html', {
			'message' : 'invalid user',
		})
	else:
		return render_to_response('home.html', {
			'message' : 'login required',
		})

	
def user_register(request):
	if request.method == 'POST':
		username		= request.REQUEST['username']
		email			= request.REQUEST['email']
		password		= request.REQUEST['password']
		first_name		= request.REQUEST['first_name']
		last_name		= request.REQUEST['last_name']
		phone_number	= request.REQUEST['phone_number']

		user = User.objects.create_user(username, email, password)
		user_profile = UserProfile.objects.create(
			user 			= user,
			first_name 		= first_name,
			last_name 		= last_name,
			phone_number 	= phone_number,
		)
		return render_to_response('home.html', {
			'message' : 'registration successful',
		})
	
	else:
		return render_to_response('user_register.html', {})


@login_required
def user_register_twitter(request):
	if request.method == 'POST':
		username	= request.REQUEST['username']
		password	= request.REQUEST['password']

		tuser = TwitterUser.objects.create(
			user		= request.user,
			username	= username,
			password	= password,
		)
		return render_to_response('home.html', {
			'message' : 'twitter integration successful',
		})

	else:
		return render_to_response('user_register_twitter.html', {})

	
def data_post(request):
	try:
		lat				= request.REQUEST['lat']
		lon				= request.REQUEST['lon']
		message			= request.REQUEST['message']

	except KeyError:
		return JsonResponse({'error' : 'missing parameter'})

	timestamp = datetime.today()

	return JsonResponse({'result' : True})

