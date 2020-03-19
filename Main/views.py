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


def user_add_error(request, initial, info):
    userlist = get_user_list(request)
    usercount = userlist.count()
    messages.info(request, info)
    form_useradd = FormUserRegistration(initial=initial)
    show_modal = True
    data = {'userlist': userlist, 'usercount': usercount, 'form_useradd': form_useradd, 'show_modal': show_modal, }
    return data

######################################################################################################################


@login_required
def user_list(request):
    if request.POST:
        username = request.POST['username']
        last_name = request.POST['last_name']
        first_name = request.POST['first_name']
        password = request.POST['password']
        password2 = request.POST['password2']
        role = request.POST['role']
        initial = {'last_name': last_name, 'first_name': first_name, 'role': role, }
        if User.objects.filter(username=username).exists():
            info = 'Пользователь ' + username + ' уже существует.'
            return render(request, 'users.html', user_add_error(request, initial, info))
        elif password != password2:
            info = 'Пароли не совпадают.'
            initial['username'] = username
            return render(request, 'users.html', user_add_error(request, initial, info))
        else:
            user = User.objects.create_user(username=username, email='', password=password2)
            user.last_name = last_name
            user.first_name = first_name
            user.save()
            profile = UserProfile()
            profile.user = user
            profile.owner = request.user
            profile.role = role
            profile.save()
            return redirect(reverse('userlist'))
    else:
        userlist = get_user_list(request)
        usercount = userlist.count()
        form_useradd = FormUserRegistration()
        return render(request, 'users.html',
                      {'userlist': userlist, 'usercount': usercount, 'form_useradd': form_useradd, })

######################################################################################################################
