from sys import prefix
from django.db import models
from django.utils.crypto import get_random_string
from django.core.exceptions import ValidationError


class LanguageName(models.Model):
    lang = models.CharField('Язык', max_length=30)
    text = models.CharField('Текст', max_length=200)

    def __str__(self) -> str:
        return f'{self.lang}: {self.text}'


class Document(models.Model):
    name = models.CharField('Название',max_length=100, blank=True, default='документ')
    lang_name = models.ManyToManyField(LanguageName, verbose_name='Название для разных языков', related_name='documents')
    file = models.FileField('Файл',blank=True)
    required = models.BooleanField('Обязателен',default=True)

    def __str__(self) -> str:
        return self.name


    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'


class Service(models.Model):
    name = models.CharField('Название',max_length=100)
    lang_name = models.ManyToManyField(LanguageName, verbose_name='Название для разных языков', related_name='service')
    average_time = models.BigIntegerField('Среднее время обслуживания в минутах',default=3, blank=True)

    prefix = models.CharField(max_length=10, blank=True)

    auto_transport = models.BooleanField('Авто перенос талона',default=False)
    service_to_auto_transport = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='employe',
        verbose_name='Услуга для переноса',
        blank=True,
        null=True
    )

    documents = models.ManyToManyField(
        to=Document,
        related_name='service',
        verbose_name='Документы',
        blank=True,
        null=True
    )

    def get_prefix(self):
        for i in range(len(self.name)):
            prefix = self.name[0:i+1]
            if not Service.objects.filter(prefix=prefix).exists():
                break
        return prefix

    def save(self, *args, **kwargs):
        if not self.prefix:
            self.prefix = self.get_prefix()
        if self.auto_transport and not self.service_to_auto_transport:
            raise ValidationError('Поле "Услуга для переноса" не может быть пустым если "Авто перенос талона" включен!')
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    
    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'


class Terminal(models.Model):
    pc_name = models.CharField(max_length=50, unique=True)
    pin = models.CharField(max_length=50)
    organization = models.CharField(max_length=100, default='RSK Bank')
    auth_token = models.CharField(max_length=200, blank=True)

    def generate_token(self,):
        token = get_random_string(length=100)
        if Terminal.objects.filter(auth_token=token).exists():
            self.generate_token()
        self.auth_token = token
        self.save()

    def __str__(self) -> str:
        return self.pc_name


    class Meta:
        verbose_name = 'Терминал'
        verbose_name_plural = 'Терминалы'


class DayOff(models.Model):
    day = models.DateField()
    
    class Meta:
        verbose_name = 'Не рабочий день'
        verbose_name_plural = 'Не рабочие дни'