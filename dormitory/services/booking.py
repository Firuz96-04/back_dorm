import datetime

from rest_framework.exceptions import ValidationError, APIException
from dormitory.models import Room, RoomType
from dormitory.models import Booking


class BookingService:

    @staticmethod
    def add_student(book, user):

        start_month = book['book_date']
        privilege = book['privilege']
        # end_month = book['book_end']
        end_month_default = datetime.date(2024, 6, 30)

        if privilege is None:
            date = end_month_default - start_month  # days
            diff_month = date.days // 30  # month
            total_price = book['student'].student_type.price * (diff_month + 1)
        else:
            total_price = 0

        book_data = Booking(**book, book_end=end_month_default, total_price=total_price, user_id=user)
        room = Room.objects.get(pk=book['room'].id)
        if room.person_count != room.room_type.place:
            room.person_count += 1
            room.save()
            book_data.save()
            if room.person_count == room.room_type.place:
                room.is_full = 1
                room.save()
            if room.room_gender == '2':
                room.room_gender = book_data.student.gender
                room.save()
        else:
            raise APIException({'room': 'В этой комнате уже нет мест'})

        return room

        # if room.room_gender == '0':
        #     room.room_gender =

        # book_data.save()  # works with signals
        #
        # try:
        #     book_data.save()
        #     if book_data.id is not None:
        #         room = Room.objects.get(pk=book_data.room.id)
        #         if room.person_count != room.room_type.place:
        #             room.person_count += 1
        #             room.save()
        #         else:
        #             raise ValidationError({'room': 'this room is full'})
        # except Exception as e:
        #     print('not savee')
