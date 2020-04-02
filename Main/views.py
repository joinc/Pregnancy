# -*- coding: utf-8 -*-

import re
import mimetypes
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import auth, User
from django.conf import settings
from django.http import HttpResponse
from datetime import datetime, timedelta
from xml.dom import minidom
from .models import UserProfile, Logs, Reference, Resident
from .forms import FormUser, FormSearch, FormUpload, FormSelect


######################################################################################################################


def admin_only(function):
    def _inner(request, *args, **kwargs):
        if request.user.is_authenticated:
            profile = get_object_or_404(UserProfile, user=request.user)
            if not profile.role == 2:
                return redirect(reverse('index'))
        else:
            return redirect(reverse('login'))
        return function(request, *args, **kwargs)
    return _inner


######################################################################################################################


@login_required
def index(request):
    # Главная страница со строкой поиска
    profile = get_object_or_404(UserProfile, user=request.user)
    context = {'profile': profile, }
    if request.POST:
        search = request.POST['find']
        context['form_search'] = FormSearch(initial={'find': search, })
        log_add(0, profile, search, None)
        snils = re.sub('\D', '', search)
        resident_list = Resident.objects.filter(snils=snils)
        if resident_list.count() > 0:
            reference_list = []
            for resident in resident_list:
                references = Reference.objects.filter(resident=resident)
                for reference in references:
                    reference_list.append(reference)
            context['reference_list'] = reference_list
        else:
            context['noresult'] = True
    else:
        context['form_search'] = FormSearch()
    return render(request, 'index.html', context)


######################################################################################################################


def login(request):
    # Вход пользователя
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
    # Выход пользователя
    auth.logout(request)
    return redirect(reverse('index'))


######################################################################################################################


def log_add(event, participan, search_string, download_xml):
    log = Logs()
    log.event = event
    log.participan = participan
    log.search_string = search_string
    log.download_xml = download_xml
    log.save()


######################################################################################################################


def get_xml_text(xmlroot, tag, default):
    result = default
    data = xmlroot.getElementsByTagName(tag)
    if len(data) > 0:
        try:
            result = data[0].firstChild.data
        except:
            pass
    return result


######################################################################################################################


def get_xml_bool(xmlroot, tag, default):
    result = default
    data = xmlroot.getElementsByTagName(tag)
    if len(data) > 0:
        try:
            if data[0].firstChild.data == 'Да':
                result = True
            if data[0].firstChild.data == 'Нет':
                result = False
        except:
            pass
    return result


######################################################################################################################


def get_xml_date(xmlroot, tag, default):
    result = default
    data = xmlroot.getElementsByTagName(tag)
    if len(data) > 0:
        try:
            result = datetime.strptime(data[0].firstChild.data, '%d.%m.%Y').date()
        except:
            pass
    return result


######################################################################################################################


def get_user_list(profile):
    if profile.role == 2:
        return UserProfile.objects.all()
    if profile.role == 1:
        return UserProfile.objects.filter(owner=profile.user)
    return None


######################################################################################################################


def user_list_context(request, initial, info):
    profile = get_object_or_404(UserProfile, user=request.user)
    userlist = get_user_list(profile)
    usercount = userlist.count()
    if info:
        messages.info(request, info)
    if initial:
        form_user = FormUser(initial=initial)
    else:
        form_user = FormUser()
    context = {'profile': profile, 'userlist': userlist, 'usercount': usercount, 'form_user': form_user, }
    return context


######################################################################################################################


def find_resident(r_first_name, r_middle_name, r_last_name, r_snils, r_birthday):

    def new_resident(n_first_name, n_middle_name, n_last_name, n_snils, n_birthday):
        resident = Resident()
        resident.first_name = n_last_name
        resident.middle_name = n_middle_name
        resident.last_name = n_first_name
        resident.birthday = n_birthday
        resident.snils = n_snils
        resident.save()
        return resident

    r_snils = re.sub('\D', '', r_snils)
    residents = Resident.objects.filter(snils=r_snils)
    new = True
    if residents.count() > 0:
        for resident in residents:
            if resident.snils == r_snils \
                    and resident.first_name == r_last_name \
                    and resident.middle_name == r_middle_name \
                    and resident.last_name == r_first_name \
                    and resident.birthday != r_birthday:
                new = True
                break
        if not new:
            return resident
    return new_resident(r_first_name, r_middle_name, r_last_name, r_snils, r_birthday)


######################################################################################################################


@login_required
def card_show(request, card_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    card = get_object_or_404(Reference, id=card_id)
    log_add(1, profile, '', card)
    snils = str(card.resident.snils)
    snils = snils[:3] + '-' + snils[3:6] + '-' + snils[6:9] + ' ' + snils[9:]
    context = {'card': card, 'snils': snils, }
    return render(request, 'card.html', context)


######################################################################################################################


@login_required
def card_print(request, card_id):
    profile = get_object_or_404(UserProfile, user=request.user)
    card = get_object_or_404(Reference, id=card_id)
    log_add(3, profile, '', card)
    context = {'card': card, }
    return render(request, 'print.html', context)


######################################################################################################################


@admin_only
def logs_list(request):
    # Выводит страницу с логами использования полязователями системы
    profile = get_object_or_404(UserProfile, user=request.user)
    context = {'profile': profile, }
    if request.POST:
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        form_select = FormSelect(request.POST)
        context['start_date'] = start_date
        context['end_date'] = end_date
        start_date = datetime.strptime(start_date, '%d.%m.%Y')
        end_date = datetime.strptime(end_date, '%d.%m.%Y') + timedelta(hours=24)
        unsort_user_data = {}
        for iuser in UserProfile.objects.all():
            user_log = Logs.objects.filter(event_date__range=[start_date, end_date]).filter(participan=iuser).count()
            if user_log > 0:
                user_name = iuser.user.id
                unsort_user_data[user_name] = user_log
        sort_user_data = sorted(unsort_user_data.items(), reverse=True, key=lambda x: x[1])
        title = ['ФИО', 'Поиск по СНИЛС', 'Просмотр карточки', 'Скачивание xml-файла', 'Печать карточки']
        user_data = [title]
        for key, value in sort_user_data:
            user = get_object_or_404(UserProfile, user=key)
            data = [user.user.get_full_name() + ' (' + str(value) + ')']
            for i in range(0, 4):
                data.append(Logs.objects.filter(event_date__range=[start_date, end_date]).filter(participan__user=key).filter(event=i).count())
            user_data.append(data)
        context['user_data'] = user_data
    else:
        end_date = datetime.now()
        month_delta = timedelta(days=30)
        start_date = end_date - month_delta
        form_select = FormSelect(initial={'start_date': start_date, 'end_date': end_date, })
    context['form_select'] = form_select
    return render(request, 'logs.html', context)


######################################################################################################################


@login_required
def xml_download(request, card_id):
    # Скачивает xml-файл, приложенный к карточке
    profile = get_object_or_404(UserProfile, user=request.user)
    card = get_object_or_404(Reference, id=card_id)
    log_add(2, profile, '', card)
    response = HttpResponse(card.xml_file.file)
    file_type = mimetypes.guess_type(card.xml_file.name)
    if file_type is None:
        file_type = 'application/octet-stream'
    response['Content-Type'] = file_type
    response['Content-Length'] = card.xml_file.size
    response['Content-Disposition'] = "attachment; filename=" + card.xml_file.name
    return response


######################################################################################################################


@admin_only
def xml_export(request):
    # Загружает xml-файлы и создает на их основе карточки
    profile = get_object_or_404(UserProfile, user=request.user)
    form_upload = FormUpload()
    context = {'profile': profile, 'form_upload': form_upload, }
    if request.POST:
        successfully = []
        for file in request.FILES.getlist('files'):
            reference = Reference()
            reference.load_owner = profile
            successfully.append(str(file))
            reference.xml_file.save(file.name, file)
            xmldoc = minidom.parse(reference.xml_file.file)
            xmldoc.normalize()
            doc = xmldoc.getElementsByTagName('Organization')[0]
            reference.organization = get_xml_text(doc, 'Org', reference.organization)
            reference.number = get_xml_text(doc, 'Number', reference.number)
            reference.issue_date = get_xml_date(doc, 'DateSpr', reference.issue_date)
            first_name = get_xml_text(doc, 'FirstName', '')
            last_name = get_xml_text(doc, 'LastName', '')
            middle_name = get_xml_text(doc, 'MiddleName', '')
            birthday = get_xml_date(doc, 'Birthdate', datetime(1900, 1, 1))
            snils = get_xml_text(doc, 'Snils', '')
            reference.resident = find_resident(first_name, middle_name, last_name, snils, birthday)
            reference.address = get_xml_text(doc, 'Address', reference.address)
            reference.early_registration = get_xml_bool(doc, 'EarlyRegistration', reference.early_registration)
            reference.period_pregnancy = get_xml_text(doc, 'PeriodPregnancy', reference.period_pregnancy)
            reference.doctor = get_xml_text(doc, 'Doctor', reference.doctor)
            reference.sign = get_xml_text(doc, 'Sign', reference.sign)
            reference.save()
        context['successfully'] = successfully
    return render(request, 'export.html', context)


######################################################################################################################


@login_required
def user_list(request):
    # Выводит страницу со списком пользователей (Администраторы видят всех, Модераторы видят только)
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
                context = user_list_context(request, None, None)
                context['toast'] = 'Создана учетная запись пользователя ' + new_user.get_full_name() + '.'
                return render(request, 'users.html', context)
            context = user_list_context(request, initial, info)
            context['show_user'] = True
            return render(request, 'users.html', context)
        elif 'blockuser' in request.POST:
            user_id = request.POST['useridblock']
            user = get_object_or_404(UserProfile, user=user_id)
            if (profile.role == 2) or (profile.role == 1 and user.owner == profile.user):
                context = user_list_context(request, None, None)
                user.blocked = True
                user.save()
                context['toast'] = 'Пользователь ' + user.user.get_full_name() + ' заблокирован.'
                return render(request, 'users.html', context)
            else:
                return redirect(reverse('userlist'))
        elif 'unblockuser' in request.POST:
            user_id = request.POST['useridunblock']
            user = get_object_or_404(UserProfile, user=user_id)
            if (profile.role == 2) or (profile.role == 1 and user.owner == profile.user):
                context = user_list_context(request, None, None)
                user.blocked = False
                user.save()
                context['toast'] = 'Пользователь ' + user.user.get_full_name() + ' разблокирован.'
                return render(request, 'users.html', context)
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
                    if not user.user.is_superuser:
                        user.user.set_password(passwd2)
                        user.user.save()
                    context = user_list_context(request, None, None)
                    context['toast'] = 'Изменен пароль для пользователя ' + user.user.get_full_name() + '.'
                    return render(request, 'users.html', context)
                context = user_list_context(request, None, info)
                context['user'] = user
                context['show_passwd'] = True
                return render(request, 'users.html', context)
            else:
                return redirect(reverse('userlist'))
        else:
            return redirect(reverse('userlist'))
    else:
        if profile.role in [1, 2]:
            context = user_list_context(request, None, None)
            return render(request, 'users.html', context)
        else:
            return redirect(reverse('index'))


######################################################################################################################
