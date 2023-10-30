from django.db import models
from dormitory.models import CustomUser, Building

# Create your models here.


class Commandant(models.Model):

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    building = models.ForeignKey(Building, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'commandant'
