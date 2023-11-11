from django.contrib.auth.models import User
from django.db import models
from enum import IntEnum


class OAuth(models.Model):
    access_token = models.CharField(max_length=128)
    refresh_token = models.CharField(max_length=256)
    expires = models.DateTimeField()

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def approved_addon_token(self) -> str:
        try:
            scope = self.scopes.get(permission_type='ADDON_USER_APPROVED')
        except self.DoesNotExist:
            raise Exception("oauth does not have user approved scope")

        return scope.resource_id

    def has_phone_number_scope(self):
        if not self.scopes.filter(permission_type='USER_PHONE').exists():
            raise Exception("oauth does not have user phone scope")


class PermissionTypes(IntEnum):
    ADDON_USER_APPROVED = 1
    USER_PHONE = 2
    ADDON_STICKY_CREATE = 3

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Scope(models.Model):
    permission_type = models.CharField(max_length=100, choices=PermissionTypes.choices())
    resource_id = models.CharField(max_length=100, null=True)
    oauth = models.ForeignKey(OAuth, on_delete=models.CASCADE, related_name="scopes", related_query_name="scope")
