# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from .choices import ROLE_CHOICES

######################################################################################################################


class FormUser(forms.Form):
    username = forms.CharField(
        label='Логин пользователя',
        widget=forms.TextInput(
            attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Введите логин пользователя', }
        ),
        required=True,
    )
    first_name = forms.CharField(
        label='Имя',
        widget=forms.TextInput(
            attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Введите имя пользователя', }
        ),
        required=True,
    )
    last_name = forms.CharField(
        label='Фамилия',
        widget=forms.TextInput(
            attrs={'type': 'text', 'class': 'form-control', 'placeholder': 'Введите фамилию пользователя', }
        ),
        required=True,
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label='Роль пользователя',
        initial=0,
        widget=forms.Select(attrs={'class': 'custom-select'}),
        required=True,
    )
    passwd1 = forms.CharField(
        label='Пароль',
        widget=forms.TextInput(
            attrs={'type': 'password', 'class': 'form-control', 'autocomplete': 'off', }
        ),
        required=True,
    )
    passwd2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.TextInput(
            attrs={'type': 'password', 'class': 'form-control', 'autocomplete': 'off', }
        ),
        required=True,
    )
    changepasswd1 = forms.CharField(
        label='Новый пароль',
        widget=forms.TextInput(
            attrs={'type': 'password', 'class': 'form-control', 'autocomplete': 'off', }
        ),
        required=True,
    )
    changepasswd2 = forms.CharField(
        label='Подтверждение нового пароля',
        widget=forms.TextInput(
            attrs={'type': 'password', 'class': 'form-control', 'autocomplete': 'off', }
        ),
        required=True,
    )