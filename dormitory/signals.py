from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
from .models import CustomUser
from commandant.models import Commandant
from accounts.models import Account
from dormitory.models import Room, Booking


@receiver(post_save, sender=CustomUser)
def creat_user_check(sender, instance, created, **kwargs):
    if created:
        print(instance.role)
        if instance.role == '3':
            print('bbbbb')
            Commandant.objects.create(user=instance)
        if instance.role == '2':
            Account.objects.create(user=instance)

    else:
        pass
        # print('not created')


@receiver(post_save, sender=Booking)
def add_room_person(sender, created, instance, **kwargs):
    pass
    # if created:
    #     room = Room.objects.get(pk=instance.room.id)
    #     room_place = room.room_type.place
    #     if room_place != room.person_count:
    #         room.person_count += 1
    #         room.save()
    #     else:
    #         raise ValidationError({'room': 'this room is full'})