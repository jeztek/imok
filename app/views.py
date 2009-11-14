from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

from core.helpers import random_string, JsonResponse
from models import User, PhoneUser, TwitterUser, Post
from twitter import twitter_post


@login_required
def home(request, message=''):

	phone_user = PhoneUser.objects.filter(user=request.user)

	try:
		twitter_user = TwitterUser.objects.get(user=request.user)
	except ObjectDoesNotExist:
		twitter_user = None

	messages = Post.objects.filter(user=request.user).order_by('-datetime')[:10]
	
	return render_to_response('home.html', {
		'message'		: message,
		'first_name' 	: request.user.first_name,
		'last_name'  	: request.user.last_name,
		'phones'	 	: phone_user,
		'twitter_user'	: twitter_user,
		'messages'		: messages,
	})


def user_login(request):
	# TODO: GET -> POST
	if request.method == 'POST':
		try:
			username = request.REQUEST['username']
			password = request.REQUEST['password']
		except KeyError:
			return render_to_response('user_login.html', {
				'message' : 'missing username or password'
			})

		user = auth.authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				auth.login(request, user)
				return home(request)

		return render_to_response('user_login.html', {
			'message' : 'invalid username or password',
		})
	else:
		return render_to_response('user_login.html', {})


def user_logout(request):
	auth.logout(request)
	return home(request)


def user_register(request):
	if request.method == 'POST':
		username		= request.REQUEST['username']
		email			= request.REQUEST['email']
		password		= request.REQUEST['password']
		repassword  	= request.REQUEST['repassword']
		first_name		= request.REQUEST['first_name']
		last_name		= request.REQUEST['last_name']

		templ = {
			'username'	 : username,
			'first_name' : first_name,
			'last_name'	 : last_name,
			'password'	 : password,
			'repassword' : repassword,
			'email'		 : email
		}

		if password != repassword:
			templ['message'] = 'Error: passwords must match'
			return render_to_response('user_register.html', templ)

		try:
			user = User.objects.create_user(
				username=username, 
				email=email, 
				password=password)
		except IntegrityError:
			templ['message'] = 'Error: username already taken'
			return render_to_response('user_register.html', templ)

		user.first_name = first_name
		user.last_name = last_name
		user.save()

		# TODO: Log user in?
		return home(request)
	
	else:
		return render_to_response('user_register.html', {})


def search(request):
	if request.method == 'POST':
		try:
			query = request.POST['query']
		except KeyError:
			return home(request, 'missing query')
		return render_to_response('search.html', {
			'query' : query,
		})
	
	else:
		return home(request)


@login_required
def user_register_phone(request):		
	if request.method == 'POST':
		try:
			phone_number = request.POST['phone_number']
			user_key = request.POST['user_key']
		except KeyError:
			return home(request, user_key)
			

		try:
			phone_user = PhoneUser.objects.get(user_key=user_key)
		except ObjectDoesNotExist:
			return home(request, 'invalid user key on registration')

		phone_user.phone_number = phone_number
		phone_user.save()

		return home(request, 'phone registered')
	else:
		user_key = random_string(5)
		while len(PhoneUser.objects.filter(user_key=user_key)) > 0:
			user_key = random_string(5)

		phone_user = PhoneUser.objects.create(
			user	= request.user,
			phone_number = "",
			user_key = user_key,
			is_valid = False,
		)

		return render_to_response('user_register_phone.html', {
			'user_key' : user_key,
		})


@login_required
def user_register_phone_delete(request, user_key):
	try:
		phone_user = PhoneUser.objects.filter(user_key=user_key)
	except ObjectDoesNotExist:
		return home(request, "invalid phone")

	phone_user.delete()
	return home(request, "phone successfully deleted")

	
@login_required
def user_register_twitter(request):
	if request.method == 'POST':
		username	= request.REQUEST['username']
		password	= request.REQUEST['password']

		if len(TwitterUser.objects.filter(username=username)) > 0:
			return home(request, 'twitter account already exists')

		tuser = TwitterUser.objects.create(
			user		= request.user,
			username	= username,
			password	= password,
		)
		return home(request, 'twitter account registered')
	
	else:
		return render_to_response('user_register_twitter.html', {})


@login_required
def user_register_twitter_delete(request):
	try:
		twitter_user = TwitterUser.objects.get(user=request.user)
		twitter_user.delete()
	except ObjectDoesNotExist:
		return home(request, 'unknown twitter account')

	return home(request, 'twitter account deleted')

	
def data_register(request, user_key):

	try:
		phone_user = PhoneUser.objects.get(user_key=user_key)
	except ObjectDoesNotExist:
		return JsonResponse({'result' : False})

	phone_user.is_valid = True
	phone_user.save()

	return JsonResponse({
		"result" 		: True,
		"first_name" 	: phone_user.user.first_name,
		"last_name" 	: phone_user.user.last_name,
	})


def data_imok(request, user_key):	
	try:
		lat				= request.REQUEST['lat']
		lon				= request.REQUEST['lon']
	except KeyError:
		return JsonResponse({'result' : False, 'error' : 'missing parameters'})

	try:
		phone = PhoneUser.objects.get(user_key=user_key)
	except ObjectDoesNotExist:
		return JsonResponse({'result' : False, 'error' : 'unknown user'})

	message			= "I'm Ok!"
	timestamp = datetime.today()
	post = Post.objects.create(
		user		= request.user,
		datetime	= timestamp,
		lat			= lat,
		lon			= lon,
		message		= message,
	)

	result = twitter_post(request.user, message)
	return JsonResponse({'result' : result})
