from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime
from django.utils import timezone
from django.db import models

from services import constants
from apps.branch.models import Branch, Window
from apps.client.models import Client
from apps.base.models import Service
from apps.eqs.models import EQS

User = get_user_model()


class Talon(models.Model):
    token = models.CharField('Токен',max_length=100, blank=True)
    status = models.CharField('Статус',max_length=100, default=constants.TALON_STATUS_WAITING)
    client_type = models.CharField('Тип клиента',max_length=100)
    client_comment = models.CharField('Комментарий клиента',max_length=100, blank=True)
    employee_comment = models.CharField('Коментарий сотрудника',max_length=200, blank=True)

    is_pensioner = models.BooleanField('Пенсионер',default=False)

    service_start = models.DateTimeField('Начало обслуживания',null=True, blank=True)
    service_end = models.DateTimeField('Конец обслуживания',null=True, blank=True)
    appointment_date = models.DateTimeField('Примерное время приема',null=True, blank=True)
    is_appointed = models.BooleanField('Назначен',default=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    operators = models.ManyToManyField(
        to=User, 
        related_name='talon', 
        verbose_name='Операторы',
        blank=True,
        )

    service = models.ForeignKey(
        to=Service,
        on_delete=models.CASCADE,
        related_name='talon',
        verbose_name='Услуга'
    )
    branch = models.ForeignKey(
        to=Branch,
        on_delete=models.CASCADE,
        related_name='talon',
        verbose_name='Филиал'
    )
    queue = models.ForeignKey(
        to=EQS,
        on_delete=models.CASCADE,
        related_name='talon',
        verbose_name='Очередь',
        blank=True,
        null=True
    )
    client = models.ForeignKey(
        to=Client,
        on_delete=models.CASCADE,
        related_name='talon',
        verbose_name='Клиент',
        blank=True,
        null=True
    )

    def create_token(self):
        prefix = f'{self.service.prefix.upper()}{self.branch.id}'
        if not Talon.objects.filter(branch=self.branch, service=self.service, appointment_date__date=self.appointment_date.date()).exists():
            number = 1
        else: 
            number = Talon.objects.filter(branch=self.branch, service=self.service).last().id
        token = f'{prefix}{number:04d}'
        return token

    def save(self, *args, **kwargs):
        
        if not EQS.objects.filter(branch=self.branch, service=self.service).exists():
            queue = EQS.objects.create(branch=self.branch, service=self.service)
        else:
            queue = EQS.objects.filter(branch=self.branch, service=self.service).first()
        self.queue = queue

        if not self.appointment_date:
            self.is_appointed = False
            today = timezone.now().date()
            if not Talon.objects.filter(branch=self.branch, service=self.service, appointment_date__date=today).exists():
                self.appointment_date = datetime.combine(today, self.branch.work_time_start)
            else:
                last_talon = Talon.objects.filter(branch=self.branch, service=self.service, appointment_date__date=today).latest('appointment_date')
                if last_talon.appointment_date < timezone.now():
                    self.appointment_date = timezone.now()
                else:
                    self.appointment_date = last_talon.appointment_date + timedelta(minutes=self.service.average_time)
        
        if self.appointment_date.time() > self.branch.work_time_end:
            raise ValidationError('На этот день очередь забита!')

        if not self.token:
            self.token = self.create_token()
            
        queue.talon_count += 1
        queue.save()

        super().save(*args, **kwargs)

        
    def __str__(self):
        return f'''{self.token}
            '''

    class Meta:
        verbose_name = 'Талон'
        verbose_name_plural = 'Талоны'


class Monitor(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='branches', null=True)
    talon = models.ForeignKey(Talon, on_delete=models.CASCADE, related_name='talons', null=True)
    window = models.ForeignKey(Window, on_delete=models.CASCADE, related_name='windows')

    def __str__(self) -> str:
        return f'{self.talon} - {self.window}'