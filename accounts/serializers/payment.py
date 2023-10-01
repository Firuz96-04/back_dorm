from rest_framework import serializers
from dormitory.models import Payment, Booking
from rest_framework.exceptions import APIException
from dormitory.serializers import BookStudentSerializer, BookSerializer

class PaymentApiSerializer(serializers.ModelSerializer):
    payed_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Payment
        fields = ('id', 'booking', 'amount', 'bill', 'comment', 'payed_date')

    def validate(self, data):
        amount = data.get('amount')
        book = Booking.objects.get(pk=data.get('booking').id)

        if amount <= 0:
            raise APIException({'amount': 'Сумма оплата должно быт больше чем 0'})
        if book.total_price < book.payed + amount:
            limit = abs(book.total_price - (book.payed + amount))
            raise APIException({'total': f'Студент переплачивает {limit}'})

        return data


class PayFilterSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    payed_date = serializers.DateTimeField(format="%d.%m.%Y %H:%M", required=False)
    bill = serializers.CharField()
    amount = serializers.CharField()
    name = serializers.CharField(source='booking__student__name')
    last_name = serializers.CharField(source='booking__student__last_name')