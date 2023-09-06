import datetime

from django.contrib.auth import authenticate
from django.db.models import Count, Sum, F, Exists, OuterRef, Q
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import mixins, viewsets, generics
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (Country, Principal, Faculty, Building, RoomType, Room, Student,
                     Booking, Privilege, CustomUser, StudentType)
from . import serializers
from rest_framework.decorators import action
from .utils import CustomPagination
from rest_framework.permissions import IsAuthenticated
from .services.booking import BookingService
from django_filters import rest_framework as filters
from .filters import StudentFilter, FreeRoomFilter, BookFilter, RoomFilter


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

    def destroy(self, request, *args, **kwargs):
        item_id = kwargs.get('pk')
        try:
            country = get_object_or_404(Country, pk=item_id)
            country.delete()
            return Response({'message': 'deleted'})
        except Exception as e:
            return Response({'message': 'error'})


class StudentTypeApi(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    queryset = StudentType.objects.all()
    serializer_class = serializers.StudentTypeSerializer


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

    def destroy(self, request, *args, **kwargs):
        item_id = kwargs.get('pk')
        try:
            faculty = get_object_or_404(Faculty, pk=item_id)
            faculty.delete()
            return Response({'message': 'deleted'})
        except Exception as e:
            return Response({'message': 'error'})


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
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = RoomFilter

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        room_id = kwargs.get('pk')
        room = get_object_or_404(Room, pk=room_id)
        serial = serializers.RoomEditSerializer(room, request.data, partial=True)
        serial.is_valid(raise_exception=True)
        serial.save()
        return Response({'data': serial.data})

    def destroy(self, request, *args, **kwargs):
        room_id = kwargs.get('pk')
        try:
            room = get_object_or_404(Room, pk=room_id)
            room.delete()
            return Response({'message': 'deleted'})
        except Exception as e:
            return Response({'message': 'error'})


class StudentView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Student.objects.order_by('-id')
    serializer_class = serializers.StudentSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = StudentFilter

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        student = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(student)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data  # pagination data
        else:
            serializer = self.get_serializer(student, many=True)
            data = serializer.data
        return Response(data)

    @action(methods=['get'], detail=False)
    def categories(self, request):
        faculty = serializers.FacultySerializer(Faculty.objects.all(), many=True)
        country = serializers.CountrySerializer(Country.objects.all(), many=True)
        student_type = serializers.StudentTypeSerializer(StudentType.objects.all(), many=True)
        return Response({'data': {
            'faculty': faculty.data,
            'country': country.data,
            'student_type': student_type.data
        }})


class BookView(mixins.ListModelMixin,
               mixins.CreateModelMixin,
               mixins.UpdateModelMixin,
               mixins.DestroyModelMixin,
               viewsets.GenericViewSet):
    serializer_class = serializers.BookSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    pagination_class = CustomPagination
    filterset_class = BookFilter

    # parser_classes = (FormParser, MultiPartParser)

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return Booking.objects.select_related('room__building', 'student__country', 'student__faculty',
                                              'user').order_by('created_at')

    def list(self, request, *args, **kwargs):
        query = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(query)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data  # pagination data
        else:
            serializer = self.get_serializer(query, many=True)
            data = serializer.data
        return Response(data)

    # def list(self, request, *args, **kwargs):
    #     query = self.filter_queryset(self.get_queryset())
    #     serial = serializers.BookSerializer(query, many=True).data
    #     return Response({'data': serial})

    def create(self, request, *args, **kwargs):
        book = serializers.BookSerializer(data=request.data)
        book.is_valid(raise_exception=True)
        book_data = BookingService.add_student(book.validated_data, self.request.user.id)
        # serial = serializers.BookSerializer(book_data)
        serial = serializers.FreeAddPlaceSerializer(book_data)
        return Response({'data': serial.data})

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


class FreePlaceApi(mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Room.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FreeRoomFilter
    pagination_class = CustomPagination

    # def list(self, request, *args, **kwargs):
    #     student = self.filter_queryset(self.get_queryset())
    #     page = self.paginate_queryset(student)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         result = self.get_paginated_response(serializer.data)
    #         data = result.data  # pagination data
    #     else:
    #         serializer = self.get_serializer(student, many=True)
    #         data = serializer.data
    #     return Response(data)

    def list(self, request, *args, **kwargs):
        free = Room.objects.select_related('building').annotate(
            free_place=F('room_type__place') - F('person_count')
        ).values('id', 'number', 'building__name', 'building_id', 'is_full', 'floor', 'room_type__place',
                 'person_count', 'free_place').order_by('building_id', 'number', 'is_full')
        query = self.filter_queryset(free)
        page = self.paginate_queryset(query)
        if page is not None:
            serializer = serializers.FreePlaceSerializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data  # pagination data
        else:
            serializer = self.get_serializer(query, many=True)
            data = serializer.data
        build_serial = serializers.BuildingSimpleSerializer(Building.objects.all(), many=True)
        # data['results'].append({'building': build_serial.data})
        data['building'] = build_serial.data
        return Response(data)

    @action(methods=['get'], detail=False)
    def find_student(self, request):
        query = request.query_params.get('search')

        if query is not None and query != '':
            students = Student.objects.annotate(
                has_booking=Exists(Booking.objects.filter(student_id=OuterRef('pk')))
            ).filter(has_booking=False).values('id', 'name', 'last_name')
            student = students.filter(Q(name__startswith=query) | Q(last_name__startswith=query))[:4]
            serial = serializers.FreeStudentSearch(student, many=True)
            return Response({'data': serial.data})
        else:
            return Response([])


class FilterStudentApi(mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    # queryset =

    @action(methods=['get'], detail=False)
    def student(self, request):
        return Response({'message': 'Ok'})


class MainDormitoryApi(mixins.ListModelMixin, generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        query = Building.objects.annotate(
            total_rooms=Count('room__id', distinct=True),
            busy_rooms=Count('room', filter=Q(room__is_full=True), distinct=True),
            free_rooms=F('total_rooms') - F('busy_rooms'),
            women=Count('room', filter=Q(room__booking__student__gender='0')),
            men=Count('room', filter=Q(room__booking__student__gender='1')),
            build_name=F('name'),
            build_id=F('id'),
            floor_size=F('floor_count'),
            all_student=Count('room__booking__student__id', distinct=True),
        ).values('build_name', 'build_id', 'floor_size', 'total_rooms', 'busy_rooms', 'free_rooms',
                 'all_student', 'men', 'women')
        serial = serializers.MainDormitorySerializer(query, many=True)
        return Response({'data': serial.data})


class CatApi(mixins.ListModelMixin, generics.GenericAPIView):

    def get(self, request, *args, **kwargs):
        faculty = serializers.FacultySerializer(Faculty.objects.all(), many=True)
        country = serializers.CountrySerializer(Country.objects.all(), many=True)
        student_type = serializers.StudentTypeSerializer(StudentType.objects.values('id', 'type'), many=True)
        return Response({'data': {
            'faculty': faculty.data,
            'country': country.data,
            'student_type': student_type.data
        }})


def test_message():
    print('message')
