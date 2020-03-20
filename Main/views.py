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
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'index.html', {'profile': profile, })

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
def user_add_error(request, initial, info):
    profile = get_object_or_404(UserProfile, user=request.user)
    userlist = get_user_list(request)
    usercount = userlist.count()
    messages.info(request, info)
    form_useradd = FormUserRegistration(initial=initial)
    show_modal = True
    data = {'profile': profile, 'userlist': userlist, 'usercount': usercount, 'form_useradd': form_useradd,
            'show_modal': show_modal, }
    return data

######################################################################################################################


@login_required
def user_role_change(request, user_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    user = get_object_or_404(UserProfile, user=user_id)
    if (profile.role == 2) or (profile.role == 1 and user.owner == profile.user):
        if user.blocked:
            user.blocked = False
            user.save()
        else:
            user.blocked = True
            user.save()
    return redirect(reverse('userlist'))


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
        initial = {'username': username, 'last_name': last_name, 'first_name': first_name, 'role': role, }
        if User.objects.filter(username=username).exists():
            del initial['username']
            return render(request, 'users.html', user_add_error(request, initial, 'Пользователь ' + username + ' уже существует.'))
        elif password != password2:
            return render(request, 'users.html', user_add_error(request, initial, 'Пароли не совпадают.'))
        elif len(password2) < 8:
            return render(request, 'users.html', user_add_error(request, initial, 'Длина пароля менее 8 символов.'))
        elif password2.isdigit():
            return render(request, 'users.html', user_add_error(request, initial, 'Пароль состоит только из цифр.'))
        elif password2 == username:
            return render(request, 'users.html', user_add_error(request, initial, 'Пароль совпадает с логином.'))
        else:
            new_user = User.objects.create_user(username=username, email='', password=password2)
            new_user.last_name = last_name
            new_user.first_name = first_name
            new_user.save()
            new_profile = UserProfile()
            new_profile.user = new_user
            new_profile.owner = request.user
            new_profile.role = role
            new_profile.save()
            return redirect(reverse('userlist'))
    else:
        profile = get_object_or_404(UserProfile, user=request.user)
        userlist = get_user_list(request)
        usercount = userlist.count()
        form_useradd = FormUserRegistration()
        return render(request, 'users.html',
                      {'profile': profile, 'userlist': userlist, 'usercount': usercount,
                       'form_useradd': form_useradd, })

######################################################################################################################
