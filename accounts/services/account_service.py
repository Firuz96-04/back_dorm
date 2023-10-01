from django.shortcuts import get_object_or_404

from dormitory.models import Booking, Payment


class PaymentService:

    @staticmethod
    def pay_logic(payment_data):
        book_id = payment_data.get('booking').id
        print(book_id, 'boook id')
        payment = Payment(**payment_data)
        payment.save()
        if payment:
            book = get_object_or_404(Booking, pk=book_id)
            book.payed += payment_data.get('amount')
            book.save()
        else:
            pass

        # print(book_id, 'book_id')
        # payment.save()
        # print(payment_data, 'payment data')
        return payment
