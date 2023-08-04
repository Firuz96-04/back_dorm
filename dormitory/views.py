import datetime

from django.contrib.auth import authenticate
from django.db.models import Count, Sum
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import mixins, viewsets, generics
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (Country, Principal, Faculty, Building, RoomType, Room, Student,
                     Booking, Privilege, CustomUser)
from . import serializers
from rest_framework.decorators import action
from .utils import CustomPagination
from rest_framework.permissions import IsAuthenticated
from .services.booking import BookingService


# from datetime import datetime


class ManagerRegisterApi(mixins.CreateModelMixin,
                         generics.GenericAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.UserSerializer

    def post(self, request, *args, **kwargs):
        user = serializers.UserSerializer(data=request.data)
        user.is_valid(raise_exception=True)
        user.save(role='2')

        return Response({'data': user.data})


# class UserRegisterApi(
#                       mixins.CreateModelMixin,
#                       generics.GenericAPIView):
#
#     def post(self, request, *args, **kwargs):
#         email = request.data.get('email')
#         password = request.data.get('password')
#         if not email or not password:
#             return Response({'please add email or password'})
#         user = authenticate(email=email, password=password)
#         if user.role.id == 3:
#             user_data = StudentLoginSerializer(user.student, many=False)
#         else:
#             user_data = UserSerializer(user, many=False)
#         print(user, 'user')
#         if user is not None:
#             refresh = RefreshToken.for_user(user)
#             refresh['user_name'] = user.name
#
#             data = {
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#                 'user': 'user_data.data'
#             }
#             return Response({'data': data})
#         return Response({'message': 'user not found'})


class CountryView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Country.objects.all()
    serializer_class = serializers.CountrySerializer
    permission_classes = (IsAuthenticated,)

    @action(methods=['get'], detail=False)
    def total(self, request, *args, **kwargs):
        country = Country.objects.annotate(
            booking_count=Count('student__booking'),
            student_count=Count('student__id'),

        )
        totals = country.aggregate(book_total=Sum('booking_count'), student_total=Sum('student_count'))
        serial = serializers.CountryCounterSerializer(country, many=True)
        return Response({'data': serial.data, 'totals': {'book_total': totals['book_total'],
                                                         'student_total': totals['student_total']}})


class PrincipalView(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Principal.objects.all()
    serializer_class = serializers.PrincipalSerializer
    permission_classes = (IsAuthenticated,)


class FacultyView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Faculty.objects.all()
    serializer_class = serializers.FacultySerializer
    permission_classes = (IsAuthenticated,)

    @action(methods=['get'], detail=False)
    def total(self, request, *args, **kwargs):
        faculty = Faculty.objects.annotate(
            booking_count=Count('student__booking'),
            student_count=Count('student__id'),
        )
        totals = faculty.aggregate(book_total=Sum('booking_count'), student_total=Sum('student_count'))
        serial = serializers.FacultyCounterSerializer(faculty, many=True)
        return Response({'data': serial.data, 'totals': {'book_total': totals['book_total'],
                                                         'student_total': totals['student_total']}})


class BuildingView(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Building.objects.all()
    serializer_class = serializers.BuildingSerializer


class RoomTypeView(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = RoomType.objects.all()
    serializer_class = serializers.RoomTypeSerializer


class RoomView(mixins.ListModelMixin,
               mixins.CreateModelMixin,
               mixins.UpdateModelMixin,
               mixins.DestroyModelMixin,
               viewsets.GenericViewSet):
    queryset = Room.objects.select_related('room_type', 'user', 'building').order_by('-id')
    serializer_class = serializers.RoomSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StudentView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Student.objects.order_by('-id')
    serializer_class = serializers.StudentSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BookView(mixins.ListModelMixin,
               mixins.CreateModelMixin,
               mixins.UpdateModelMixin,
               mixins.DestroyModelMixin,
               viewsets.GenericViewSet):
    serializer_class = serializers.BookSerializer
    # parser_classes = (FormParser, MultiPartParser)
    def get_queryset(self):
        return Booking.objects.select_related('room__building', 'student__country', 'student__faculty',
                                              'user').order_by('created_at')

    def list(self, request, *args, **kwargs):
        serial = serializers.BookSerializer(self.get_queryset(), many=True).data
        return Response({'data': serial})

    def create(self, request, *args, **kwargs):

        book = serializers.BookSerializer(data=request.data)
        book.is_valid(raise_exception=True)
        # book.save()
        book_ser = BookingService()
        nb = book_ser.add_student(book.validated_data)
        print(nb, 'result')
        return Response({'data': book.data})

    def update(self, request, *args, **kwargs):
        sana = datetime.date(2024, 6, 13)
        sana2 = datetime.date.today()

        res = (sana.year - sana2.year) * 12 + (sana.month - sana2.month)
        print(res)
        return Response('message')


class PrivilegeView(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Privilege.objects.all()
    serializer_class = serializers.PrivilegeSerializer

    def create(self, request, *args, **kwargs):
        privilege = serializers.PrivilegeSerializer(data=request.data)
        privilege.is_valid(raise_exception=True)
        privilege.save()
        headers = self.get_success_headers(privilege.data)
        # print(headers, 'headers')
        # print(headers.keys())
        return Response({'data': privilege.data, 'headers': headers})


class TesView(viewsets.ModelViewSet):
    queryset = Privilege.objects.all()
    serializer_class = serializers.PrivilegeSerializer
