from django.db import models
from base.models import LanguageName, Service, Terminal


class Branch(models.Model):
    city = models.CharField('Город', max_length=200)
    address = models.CharField('Адрес', max_length=200)
    work_time_start = models.TimeField('Начало рабочего дня')
    work_time_end = models.TimeField('Конец рабочего дня')

    lang_name = models.ManyToManyField(
        LanguageName, 
        verbose_name='Название для разных языков', 
        related_name='branch'
    )
    terminal = models.ForeignKey(
        to=Terminal,
        on_delete=models.CASCADE,
        related_name='branch',
        verbose_name='Терминал',
        null=True,
        blank=True
    )
    service = models.ManyToManyField(
        to=Service,
        related_name='branch',
        verbose_name='Услуги',
    )

    def __str__(self):
        return f'{self.city} : {self.address}'

    class Meta:
        verbose_name = 'Филиал'
        verbose_name_plural = 'Филиалы'


class Window(models.Model):
    branch = models.ForeignKey(
        to=Branch,
        on_delete=models.CASCADE,
        related_name='windows',
        verbose_name='Филиал',
        help_text="Выберите филиал"
    )
    number = models.IntegerField("Номер окна")

    def __str__(self) -> str:
        return f'{self.branch} - {self.number} - окно'



class RunningString(models.Model):
    title = models.CharField(max_length=50)
    text = models.TextField()

    def __str__(self) -> str:
        return self.title


class Advertisement(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='ad_images/', blank=True)

    def __str__(self) -> str:
        return self.title