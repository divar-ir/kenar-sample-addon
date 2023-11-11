from django.contrib.auth.models import User
from django.db import models


class VerifiedPost(models.Model):
    user = models.ForeignKey(to=User, to_field='username', on_delete=models.CASCADE)
    post_token = models.CharField(max_length=20, unique=True)
    postal_code = models.CharField(max_length=20, db_index=True)



