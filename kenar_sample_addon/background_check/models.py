from enum import IntEnum

from django.contrib.auth.models import User
from django.db import models

from kenar_sample_addon.background_check.clients.estl import estl_client


class Status(IntEnum):
    IN_REVIEW = 1
    ACCEPTED = 2
    REJECTED = 3
    UNKNOWN = 4

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

    @classmethod
    def from_estl(cls, s: str) -> "Status":
        match s:
            case "تایید شده":
                return cls.ACCEPTED
            case "بررسی مجدد":
                return cls.REJECTED
            case "در حال بررسی":
                return cls.IN_REVIEW
            case _:
                return cls.UNKNOWN


class BackgroundCheck(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    family_name = models.CharField(max_length=100)
    national_id_hash = models.CharField(max_length=200, db_index=True)

    status = models.CharField(choices=Status.choices(), max_length=100, db_index=True)

    check_date = models.DateField(db_index=True)
    access_token = models.CharField(max_length=512)

    def persian_check_date_str(self) -> str:
        return estl_client.get_jalali_str_from_datetime(self.check_date)
