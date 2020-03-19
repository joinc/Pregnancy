# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import auth, User
from django.conf import settings
from .models import UserProfile
from .forms import FormUserRegistration

######################################################################################################################


@login_required
def index(request):
    return render(request, 'index.html', )

######################################################################################################################


def login(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)
            #return redirect(request.META.get('HTTP_REFERER'))
            return redirect(settings.SUCCESS_URL)
        else:
            messages.info(request, 'Не правильно введенные данные')
            return redirect(reverse('login'))
    else:
        return render(request, 'login.html', )

######################################################################################################################


def logout(request):
    auth.logout(request)
    return redirect(reverse('index'))

######################################################################################################################


@login_required
def get_user_list(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if profile.role == 2:
        return UserProfile.objects.all()
    if profile.role == 1:
        return UserProfile.objects.filter(owner=profile.user)
    return None

######################################################################################################################


@login_required
def user_list(request):
    userlist = get_user_list(request)
    usercount = userlist.count()
    form_useradd = FormUserRegistration()
    return render(request, 'users.html',
                  {'userlist': userlist, 'usercount': usercount, 'form_useradd': form_useradd, })

######################################################################################################################


@login_required
def user_add(request):
    if request.POST:
        username = request.POST['username']
        last_name = request.POST['last_name']
        first_name = request.POST['first_name']
        password = request.POST['password']
        password2 = request.POST['password2']
        role = request.POST['role']
        if User.objects.filter(username=username).exists():
            messages.info(request, 'Пользователь ' + username + ' уже существует.')
            userlist = get_user_list(request)
            usercount = userlist.count()
            form_useradd = FormUserRegistration()
            show_modal = True
            return render(request, 'users.html',
                      {'userlist': userlist, 'usercount': usercount, 'form_useradd': form_useradd,
                       'show_modal': show_modal, })
        if password != password2:
            messages.info(request, 'Пароли не совпадают.')

    #form_useradd = FormUserRegistration(request.POST)
    #username = form_useradd.username

    '''
    if User.objects.filter(username=form_useradd.username):
        messages.info(request, 'Пользователь с данным логином уже существует.')
    else:
        #if form_useradd.is_valid():
        username = form_useradd.username
        email = ''
        password = form_useradd.password
        new_user = User.objects.create_user(username, email, password)
        new_user.save()
        #if form_useradd.password != form_useradd.password2:
    '''
    return redirect(reverse('index'))