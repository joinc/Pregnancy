# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import auth, User
from django.conf import settings
from .models import UserProfile
from .forms import FormUser

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
            profile = get_object_or_404(UserProfile, user=user)
            if profile.blocked:
                messages.info(request, 'Выша учетная запись заблокирована, обратитесь к администратору.')
                return redirect(reverse('login'))
            else:
                auth.login(request, user)
                return redirect(request.POST['next'])
        else:
            messages.info(request, 'Не правильно введенные данные')
            return redirect(reverse('login'))
    else:
        if request.GET.get('next'):
            return render(request, 'login.html', {'next': request.GET.get('next')})
        else:
            return render(request, 'login.html', {'next': settings.SUCCESS_URL})

######################################################################################################################


def logout(request):
    auth.logout(request)
    return redirect(reverse('index'))

######################################################################################################################


def get_user_list(profile):
    if profile.role == 2:
        return UserProfile.objects.all()
    if profile.role == 1:
        return UserProfile.objects.filter(owner=profile.user)
    return None

######################################################################################################################


def user_list_data(request, initial, info):
    profile = get_object_or_404(UserProfile, user=request.user)
    userlist = get_user_list(profile)
    usercount = userlist.count()
    if info:
        messages.info(request, info)
    if initial:
        form_user = FormUser(initial=initial)
    else:
        form_user = FormUser()
    data = {'profile': profile, 'userlist': userlist, 'usercount': usercount, 'form_user': form_user, }
    return data

######################################################################################################################

@login_required
def user_list(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.POST:
        if "adduser" in request.POST:
            username = request.POST['username']
            last_name = request.POST['last_name']
            first_name = request.POST['first_name']
            passwd1 = request.POST['passwd1']
            passwd2 = request.POST['passwd2']
            role = request.POST['role']
            initial = {'username': username, 'last_name': last_name, 'first_name': first_name, 'role': role, }
            if User.objects.filter(username=username).exists():
                del initial['username']
                info = 'Пользователь ' + username + ' уже существует.'
            elif passwd1 != passwd2:
                info = 'Пароли не совпадают.'
            elif len(passwd2) < 8:
                info = 'Длина пароля менее 8 символов.'
            elif passwd2.isdigit():
                info = 'Пароль состоит только из цифр.'
            elif passwd2 == username:
                info = 'Пароль совпадает с логином.'
            else:
                new_user = User.objects.create_user(username=username, email='', password=passwd2)
                new_user.last_name = last_name
                new_user.first_name = first_name
                new_user.save()
                new_profile = UserProfile()
                new_profile.user = new_user
                new_profile.owner = request.user
                new_profile.role = role
                new_profile.save()
                data = user_list_data(request, None, None)
                data['toast'] = 'Создана учетная запись пользователя ' + new_user.get_full_name() + '.'
                return render(request, 'users.html', data)
            data = user_list_data(request, initial, info)
            data['show_user'] = True
            return render(request, 'users.html', data)
        elif 'blockuser' in request.POST:
            user_id = request.POST['useridblock']
            user = get_object_or_404(UserProfile, user=user_id)
            if (profile.role == 2) or (profile.role == 1 and user.owner == profile.user):
                data = user_list_data(request, None, None)
                user.blocked = True
                user.save()
                data['toast'] = 'Пользователь ' + user.user.get_full_name() + ' заблокирован.'
                return render(request, 'users.html', data)
            else:
                return redirect(reverse('userlist'))
        elif 'unblockuser' in request.POST:
            user_id = request.POST['useridunblock']
            user = get_object_or_404(UserProfile, user=user_id)
            if (profile.role == 2) or (profile.role == 1 and user.owner == profile.user):
                data = user_list_data(request, None, None)
                user.blocked = False
                user.save()
                data['toast'] = 'Пользователь ' + user.user.get_full_name() + ' разблокирован.'
                return render(request, 'users.html', data)
            else:
                return redirect(reverse('userlist'))
        elif 'changepassword' in request.POST:
            passwd1 = request.POST['changepasswd1']
            passwd2 = request.POST['changepasswd2']
            user_id = request.POST['useridpassword']
            user = get_object_or_404(UserProfile, user=user_id)
            if (profile.role == 2) or (profile.role == 1 and user.owner == profile.user):
                if passwd1 != passwd2:
                    info = 'Пароли не совпадают.'
                elif len(passwd2) < 8:
                    info = 'Длина пароля менее 8 символов.'
                elif passwd2.isdigit():
                    info = 'Пароль состоит только из цифр.'
                elif passwd2 == user.user.get_username():
                    info = 'Пароль совпадает с логином.'
                else:
                    user.user.set_password(passwd2)
                    user.user.save()
                    data = user_list_data(request, None, None)
                    data['toast'] = 'Изменен пароль для пользователя ' + user.user.get_full_name() + '.'
                    return render(request, 'users.html', data)
                data = user_list_data(request, None, info)
                data['user'] = user
                data['show_passwd'] = True
                return render(request, 'users.html', data)
            else:
                return redirect(reverse('userlist'))
        else:
            return redirect(reverse('userlist'))
    else:
        if profile.role in [1, 2]:
            data = user_list_data(request, None, None)
            return render(request, 'users.html', data)
        else:
            return redirect(reverse('index'))

######################################################################################################################
