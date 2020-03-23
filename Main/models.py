from django.db import models
from django.contrib.auth.models import User
from .choices import ROLE_CHOICES, EVENT_CHOICES

######################################################################################################################


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, )
    role = models.SmallIntegerField('Роль', choices=ROLE_CHOICES, default=0, null=False, blank=False, )
    owner = models.ForeignKey(User, verbose_name='Создатель учетной записи', null=True, related_name='Owner',
                              on_delete=models.SET_NULL, )
    create_date = models.DateTimeField('Дата создания учетной записи', auto_now_add=True, null=True, )
    blocked = models.BooleanField('Состояние учетной записи, заблокирована или нет', default=False)

    def __str__(self):
        return '{0}'.format(self.user.get_full_name())

    class Meta:
        ordering = 'blocked', '-role', 'user',
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
        managed = True

######################################################################################################################


class Resident(models.Model):
    first_name = models.CharField('Имя', max_length=32, default='', )
    last_name = models.CharField('Фамилия', max_length=32, default='', )
    middle_name = models.CharField('Отчество', max_length=32, default='', )
    birthday = models.DateField('Дата рождения', null=True, )
    snils = models.CharField('СНИЛС', max_length=11, default='', )

    def __str__(self):
        return '{0} {1} {2}'.format(self.last_name, self.first_name, self.middle_name)

    class Meta:
        ordering = 'last_name', 'first_name',
        verbose_name = 'Гражданка'
        verbose_name_plural = 'Гражданки'
        managed = True

######################################################################################################################


class Reference(models.Model):
    load_owner = models.ForeignKey(UserProfile, verbose_name='Создатель карточки', null=True,
                                   related_name='Load_Owner', on_delete=models.SET_NULL, )
    load_date = models.DateTimeField('Дата создания карточки', auto_now_add=True, null=True, )
    organization = models.CharField('Наименование медицинской организации, выдавшей справку', max_length=256,
                                    default='', )
    number = models.CharField('Номер справки', max_length=32, default='', )
    issue_date = models.DateField('Дата выдачи справки', null=True, )
    resident = models.ForeignKey(Resident, verbose_name='Гражданка', null=True, related_name='Resident',
                                 on_delete=models.SET_NULL, )
    address = models.CharField('Адрес места жительства', max_length=512, default='', )
    early_registration = models.BooleanField('Факт постановки на учет в ранние сроки беременности', default=False, )
    period_pregnancy = models.CharField('Срок беременности (количество недель)', max_length=3, )
    doctor = models.CharField('ФИО врача', max_length=128, default='', )
    sign = models.CharField('Электронная подпись', max_length=128, default='', )
    xml_file = models.FileField('XML файл', upload_to='%Y/%m/%d', null=False, )

    def __str__(self):
        return '{0}'.format(self.resident)

    class Meta:
        ordering = 'load_date', 'resident',
        verbose_name = 'Справка'
        verbose_name_plural = 'Справки'
        managed = True

######################################################################################################################


class Logs(models.Model):
    event = models.SmallIntegerField('Событие', choices=EVENT_CHOICES, default=0, null=False, blank=False, )
    participan = models.ForeignKey(UserProfile, verbose_name='Субъект события', null=True, related_name='Participan',
                                   on_delete=models.SET_NULL, )
    event_date = models.DateTimeField('Дата события', auto_now_add=True, null=True, )
    search_string = models.CharField('Поисковый запрос', max_length=256, default='', )
    download_xml = models.ForeignKey(Reference, verbose_name='Скачанный файл xml', null=True,
                                     related_name='DownloadXML', on_delete=models.SET_NULL, )

    def __str__(self):
        return '{0}'.format(self.event_date)

    class Meta:
        ordering = 'event_date',
        verbose_name = 'Логи'
        verbose_name_plural = 'Логи'
        managed = True

######################################################################################################################
