from django.db import models

from base.models import Service
from branch.models import Branch


class EQS(models.Model):
    description = models.CharField('Описание',max_length=100,blank=True)

    talon_count = models.PositiveBigIntegerField('Количество всех талонов очереди',default=0)

    service = models.ForeignKey(
        to=Service,
        on_delete=models.CASCADE,
        related_name='eqs',
        verbose_name='Услуга'
    )
    branch = models.ForeignKey(
        to=Branch,
        on_delete=models.CASCADE,
        related_name='eqs',
        verbose_name='Филиал'
    )

    def __str__(self):
        return f'{self.branch},{self.service} Очередь'


    class Meta:
        verbose_name = 'Очередь'
        verbose_name_plural = 'Очереди'