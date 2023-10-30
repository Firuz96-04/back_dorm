import datetime
from datetime import timedelta
from rest_framework.exceptions import ValidationError, APIException
from dormitory.models import Room, RoomType
from dormitory.models import Booking


class BookingService:

    @staticmethod
    def add_student(book, user):

        start_month = book['book_date']
        privilege = book['privilege']
        # end_month = book['book_end']
        # end_month_default = datetime.date(2024, 6, 30)
        end_month_default = "2024-6-30"

        date1 = datetime.datetime.strptime(end_month_default, "%Y-%m-%d")
        date2 = datetime.datetime.strptime(str(start_month), "%Y-%m-%d")

        if privilege is None:
            # date = end_month_default - start_month  # days
            # diff_month = date.days // 30  # month
            diff_month = (date1.year - date2.year) * 12 + date1.month - date2.month
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

    @staticmethod
    def un_booking(book, end_date):
        book_end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        book_start = book.book_date

        current_date = book_start
        total_31 = 0
        feb_add_day = 0
        feb_last_day = 0

        if book_end.day == 31:
            finish_end = book_end - timedelta(1)
        else:
            finish_end = book_end

        while current_date <= finish_end:
            if current_date.day == 31:
                total_31 += 1
            current_date += timedelta(days=1)
            if current_date.month == 2:
                next_month = (current_date.month % 12) + 1
                feb_last_day = (datetime.datetime(current_date.year, next_month, 1) - timedelta(days=1)).day
        if feb_last_day in [28, 29]:
            feb_add_day = 30 - feb_last_day

        total_days = (finish_end - book_start).days
        day_price = (total_days + feb_add_day + 1) * book.student.student_type.day - total_31 * book.student.student_type.day
        book.book_end = book_end
        book.total_price = day_price
        book.status_id = 2
        book.save()

        room = Room.objects.get(pk=book.room_id)
        room.person_count -= 1
        room.save()
        if room.person_count == 0:
            room.is_full = 0
            room.room_gender = 2
            room.save()

        return room


    @staticmethod
    def resettle():
        pass