from django.db import models
# from django.contrib.auth import get_user_model
from dormitory.models import CustomUser
# Create your models here.


class Account(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)