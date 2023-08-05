import datetime

from rest_framework.exceptions import ValidationError
from dormitory.models import Room, RoomType
from dormitory.models import Booking


class BookingService:

    @staticmethod
    def add_student(book, user):
        start_month = book['book_date']
        end_month = book['book_end']
        end_month_default = datetime.date(2024, 7, 30)
        date = end_month_default - start_month # days
        diff_month = date.days // 30 # month
        total_price = book['student'].student_type.price * diff_month

        book_data = Booking(**book, total_price=total_price, user_id=user)
        book_data.save()
        return book_data
