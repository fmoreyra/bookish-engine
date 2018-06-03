from datetime import date
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext as _

from .career import CAREER


class CustomUser(AbstractUser):
    transcript = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('Transcript'),
        blank=True
    )
    id_number = models.CharField(
        max_length=255,
        verbose_name=_('ID Number'),
        unique=True,
        blank=True
    )
    birth_date = models.DateField(
        verbose_name=_('Birth date'),
        blank=True,
        null=True
    )
    career = models.CharField(
        max_length=255,
        choices=CAREER,
        default=CAREER[0][0],
        verbose_name=_('Career')
    )

    REQUIRED_FIELDS = ['id_number', 'email']

    @property
    def full_name(self):
        return "{0}, {1}".format(
            self.last_name.upper(),
            self.first_name
        )

    @property
    def validation_email(self):
        return self

    @property
    def age(self):
        delta = (date.today() - parse_datetime(self.birth_date))
        return int(delta.days / 365.2425)
