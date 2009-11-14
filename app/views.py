from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

from core.helpers import JsonResponse
from models import User, TwitterUser, Post
from twitter import twitter_post


def home(request):
    return render_to_response('home.html', {})


def user_login(request):
    # TODO: GET -> POST
    if request.method == 'POST':
        try:
            username = request.REQUEST['u']
            password = request.REQUEST['p']
        except KeyError:
            return render_to_response('user_login.html', {
                    'message' : 'invalid username or password'
                    })

        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return render_to_response('home.html', {
                        'message' : 'login successful',
                        })

            return render_to_response('user_login.html', {
                    'message' : 'invalid user',
                    })
    else:
        return render_to_response('user_login.html', {
                'message' : 'login required',
                })

	
def user_register(request):
    if request.method == 'POST':
        username		= request.REQUEST['username']
        email			= request.REQUEST['email']
        password		= request.REQUEST['password']
        repassword              = request.REQUEST['repassword']
        first_name		= request.REQUEST['first_name']
        last_name		= request.REQUEST['last_name']

        templ = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'password': password,
            'repassword': repassword,
            'email': email
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

        return render_to_response('home.html', {
                'message' : 'registration successful',
		})
	
    else:
        return render_to_response('user_register.html', {})


@login_required
def user_register_phone(request):
    pass

@login_required
def user_register_twitter(request):
    if request.method == 'POST':
        username	= request.REQUEST['username']
        password	= request.REQUEST['password']

        tuser = TwitterUser.objects.create(
            user	= request.user,
            username	= username,
            password	= password,
	)
        return render_to_response('home.html', {
                'message' : 'twitter integration successful',
	       })

    else:
        return render_to_response('user_register_twitter.html', {})

@login_required
def data_post(request):
    try:
        lat				= request.REQUEST['lat']
        lon				= request.REQUEST['lon']
        message			= request.REQUEST['message']
    except KeyError:
        return JsonResponse({'error' : 'missing parameter'})

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

