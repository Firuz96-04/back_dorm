from rest_framework.exceptions import ValidationError
from dormitory.models import Room, RoomType


class BookingService:

    def add_count(self, book):
        room = Room.objects.get(pk=book)
        room_place = room.room_type.place
        if room_place != room.person_count:
            room.person_count += 1
            room.save()
        else:
            raise ValidationError({'room': 'this room is full'})

        # if not room.is_full:
        #     room.person_count += 1
        #     room.save()
        #     print(room.person_count)
        #     print('hello')

        # raise ValidationError('erorr')
