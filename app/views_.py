from datetime import datetime

try:
  from django.utils.safestring import mark_safe
except ImportError:
  def mark_safe(s):
    return s
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

from core.helpers import random_string, JsonResponse
from models import User, UserProfile, RegisteredEmail, Post


def intro(request):
        
@login_required
def home(request, message=''):

    # emails widget
    emails = RegisteredEmail.objects.filter(user=request.user)

    # recent messages widget
    posts = Post.objects.filter(user=request.user).order_by('-datetime')

    if emails.count() == 0:
        banner = mark_safe('You must <a href="/email">add email contacts</a> or no one will get your messages.')
    return render_to_response('home.html', {
        'user'  : request.user,
        'profile' : request.user.get_profile(),
        'emails' : emails,
        'posts' : posts,
        'banner' : banner,
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

        UserProfile.objects.create(
            user=user,
            userKey="0",
            phoneNumber="555-555-5555",
            tz="US/Pacific",
        )
        # TODO: Log user in?
        return home(request)
	
    else:
        return render_to_response('user_register.html', {})

