from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins, viewsets, serializers
from dormitory.models import Payment
from dormitory.utils import CustomPagination
from .serializers.payment import PaymentApiSerializer, PayFilterSerializer
from accounts.services.account_service import PaymentService
from rest_framework.permissions import IsAuthenticated
from django.db.models import F, Q, Sum
from datetime import datetime

# Create your views here.


class PaymentApi(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 viewsets.GenericViewSet):
    serializer_class = PaymentApiSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CustomPagination

    def get_queryset(self):
        book_id = self.request.query_params.get('book_id')
        return Payment.objects.filter(booking=book_id)

    def create(self, request, *args, **kwargs):
        payment = PaymentApiSerializer(data=request.data)
        payment.is_valid(raise_exception=True)
        PaymentService.pay_logic(payment.validated_data)
        return Response({'data': payment.data})

    @action(methods=['get'], detail=False)
    def pay_list(self, request):
        query = request.query_params
        date_start = query.get('start_date')
        date_end = query.get('end_date')
        full_name = query.get('full_name')
        payment = Payment.objects.filter(payed_date__range=(date_start, date_end))\
            .values('id', 'amount', 'bill', 'booking__student__name', 'booking__student__last_name', 'payed_date')\
            .order_by('-payed_date')
        total_sum = payment.aggregate(Sum('amount'))
        page = self.paginate_queryset(payment)
        if page is not None:
            serializer = PayFilterSerializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data  # pagination data
        else:
            serializer = PayFilterSerializer(query, many=True)
            data = serializer.data
        data['total_sum'] = total_sum['amount__sum']
        return Response(data)