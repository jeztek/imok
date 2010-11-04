from datetime import datetime
import random
import hmac, hashlib, base64

try:
    from django.utils.safestring import mark_safe
except ImportError:
    def mark_safe(s):
        return s
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from django.core import validators
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

from core.helpers import random_string, JsonResponse
from models import User, UserProfile, RegisteredEmail, Post


from django import forms
class SignupForm(forms.Form):
    email  = forms.EmailField()
    firstName = forms.CharField()
    lastName = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    
def intro(request):
    return render_to_response('intro.html', {})


def about(request):
    return render_to_response('about.html', {})


def getInvolved(request):
    return render_to_response('getInvolved.html', {})


def message(request):
    return render_to_response('message.html', {})


def unsubscribe(request):
    try:
        hashKey = request.REQUEST['id']
    except KeyError:
        return HttpResponseRedirect('/')

    try:
        email = RegisteredEmail.objects.get(hashKey=hashKey)
    except ObjectDoesNotExist:
        return render_to_response('404Error.html', {})

    email.isBlocked = True
    email.save()

    user = User.objects.get(user=email.user)

    return render_to_response('unsubscribe.html', {
        'email' : email.email,
        'user'  : user,
    })


def login(request):
    if request.method == 'GET':
        return render_to_response('login.html', {})
    elif request.method == 'POST':
        try:
            email = request.REQUEST['email']
            password = request.REQUEST['password']
        except KeyError:
            return render_to_response('login.html', {
                'banner' : 'Missing username or password',
            })
        user = auth.authenticate(username=email, password=password)
        if user is not None:
            if user.is_active:
                auth.login(request, user)
                return home(request)

    return render_to_response('login.html', {
        'banner' : 'Invalid username or password',
    })


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')


def signup(request):
    if request.method == 'GET':
        return HttpResponseRedirect('/login/')

    elif request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            firstName = form.cleaned_data['firstName']
            lastName = form.cleaned_data['lastName']
            password = form.cleaned_data['password']

            try:
                user = User.objects.create_user(email, email, password)
                user.first_name = firstName
                user.last_name = lastName
                user.save()

                UserProfile.objects.create(
                    user=user,
                    userKey = str('%016x' % random.getrandbits(64)),
                    tz="US/Pacific",
                )
            except IntegrityError:
                return render_to_response('login.html', {
                    'banner' : 'user already exists',
                })
            
            user = auth.authenticate(username=email, password=password)
            auth.login(request, user)
            return home(request)
                
    return render_to_response('login.html', {
        'banner' : 'uh oh',
    })
    
    
@login_required
def home(request, banner=''):

    emails = RegisteredEmail.objects.filter(user=request.user)
    posts  = Post.objects.filter(user=request.user).order_by('-datetime')

    if emails.count() == 0:
        banner = mark_safe('You must <a href="/email/">add email contacts</a> or no one will get your messages.')

    return render_to_response('home.html', {
        'user'    : request.user,
        'profile' : request.user.get_profile(),
        'emails'  : emails,
        'posts'   : posts,
        'banner'  : banner,
    })


@login_required
def email(request):
    if request.method == 'GET':
        emails = RegisteredEmail.objects.filter(user=request.user, isBlocked=False).order_by('email')
        return render_to_response('registerEmail.html', {
            'emails' : emails,
        })

    elif request.method == 'POST':
        email = request.REQUEST['email']
        emailError = None
        try:
            validators.validate_email(email)

            if RegisteredEmail.objects.filter(user=request.user, email=email).count() > 0:
                emailError = "Email address already registered or unsubscribed."
            else:
                RegisteredEmail.objects.create(
                    hashKey   = RegisteredEmail.generateHashKey(email),
                    user      = request.user,
                    email     = email,
                    isBlocked = False,
                )                
        except validators.ValidationError, exc:
            emailError = 'Enter a valid email address'

        emails = RegisteredEmail.objects.filter(user=request.user, isBlocked=False).order_by('email')
        return render_to_response('registerEmail.html', {
            'emailError' : emailError,
            'emails' : emails,
        })


@login_required
def emailRemove(request):
    if request.method == 'POST':
        email = request.REQUEST['email']
        returnAddr = request.REQUEST['returnAddr']
        
        dbemail = RegisteredEmail.objects.get(user=request.user, email=email)
        dbemail.delete()

        return HttpResponseRedirect(returnAddr)


@login_required
def profileEdit(request):
    if request.method == 'GET':
        return render_to_response('editProfile.html', {})


@login_required
def profileDelete(request):
    if request.method == 'GET':
        return render_to_response('deleteProfile.html', {})
    elif request.method == 'POST':
        Post.objects.filter(user=request.user).delete()
        RegisteredEmail.objects.filter(user=request.user).delete()
        UserProfile.objects.get(user=request.user).delete()
        request.user.delete()
        auth.logout(request)
        return HttpResponseRedirect('/profile/deleted/')


@login_required
def profileDeleted(request):
    return render_to_response('deletedProfile.html', {})


@login_required
def download(request):
    return render_to_response('download.html', {})


def m_login(request):
    try:
        email = request.REQUEST['email']
        password = request.REQUEST['password']
    except KeyError:
        return JsonResponse({
            'result'     : "error",
            'message'    : "missing email or password",
            'auth_token' : None,
        })

    user = auth.authenticate(username=email, password=password)
    if user == None:
        return JsonResponse({
            'result'     : "error",
            'message'    : "Invalid email or password",
            'auth_token' : None,
        })
    return JsonResponse({
        'result'     : "ok",
        'message'    : 'login successful',
        'auth_token' : user.get_profile().userKey,
    })


def signatureIsValid(key, data, signature):
    h = hmac.new(key, data, hashlib.sha1)
    return base64.b64encode(h.digest()) == signature
    

def m_post(request):
    try:
        email = request.REQUEST['email']
        timestamp = request.REQUEST['timestamp']
        message = request.REQUEST['message']            
    except KeyError:
        return JsonResponse({
            'result'  : "error",
            'message' : "missing parameter"
        })

    latitude = longitude = None
    if 'latitude' in request.REQUEST and 'longitude' in request.REQUEST:
        latitude = request.REQUEST['latitude']
        longitude = request.REQUEST['longitude']

    try:
        user = User.objects.get(email=email)
        profile = user.get_profile()
    except ObjectDoesNotExist:
        return JsonResponse({'result' : "error", 'message' : "unknown user"})

    if signatureIsValid(profile.userKey, request.raw_post_data, \
                        request.META['HTTP_X_IMOK_SIGNATURE'])
        post = Post.fromText(message)
        post.user = user
        post.datetime = datetime.now()
        post.postId = Post.generatePostId()
        post.save()
        
        return JsonResponse({'result' : "ok", 'message' : message})

    return JsonResponse({'result' : "error", 'message' : "invalid signature"})
