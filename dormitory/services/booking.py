import datetime

from rest_framework.exceptions import ValidationError
from dormitory.models import Room, RoomType
from dormitory.models import Booking


class BookingService:

    # def add_count(self, book):
    #     room = Room.objects.get(pk=book)
    #     room_place = room.room_type.place
    #     if room_place != room.person_count:
    #         room.person_count += 1
    #         room.save()
    #     else:
    #         raise ValidationError({'room': 'this room is full'})
    @staticmethod
    def add_student(book):
        start_month = book['book_date']
        end_month = book['book_end']
        end_month_default = datetime.date(2024, 7, 25)
        date = end_month_default - start_month # days
        diff_month = date.days // 30 # month

        total_price = book['student'].student_type.price * diff_month
        # print(total_price)
        dook = Booking(**book, total_price=total_price)
        dook.save()
        return dook
        # if not room.is_full:
        #     room.person_count += 1
        #     room.save()
        #     print(room.person_count)
        #     print('hello')

        # raise ValidationError('erorr')
