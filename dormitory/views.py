import datetime

from django.contrib.auth import authenticate
from django.db.models import Count, Sum, F, Exists, OuterRef, Q, ProtectedError
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins, viewsets, generics
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (Country, Principal, Faculty, Building, RoomType, Room, Student,
                     Booking, Privilege, CustomUser, Company, Group, StudentType)
from . import serializers
from rest_framework.decorators import action
from .utils import CustomPagination
from rest_framework.permissions import IsAuthenticated
from .services.booking import BookingService
from django_filters import rest_framework as filters
from .filters import StudentFilter, FreeRoomFilter, BookFilter, RoomFilter
from .utils import export_to_excel
from rest_framework_simplejwt.views import TokenRefreshView
import time
from datetime import datetime, timedelta
import calendar


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = serializers.CustomTokenRefreshSerializer


# from datetime import datetime
# class CustomTokenRefreshSerializer(TokenRefreshSerializer):
#     def validate(self, attrs):
#         # Add custom logic here if needed
#         # For example, you can check for certain conditions or permissions
#         return super().validate(attrs)
#
#
# class CustomTokenRefreshView(TokenRefreshView):
#
#     def post(self, request, *args, **kwargs):
#         # Call the parent class's post method to refresh the token
#         print('sss', 'errer')
#         response = super().post(request, *args, **kwargs)
#         print(response, 'response')
#         # Check if the token refresh was successful
#         if response.status_code == status.HTTP_200_OK:
#             # You can add custom logic here if needed
#             print(response, 'response')
#             # For example, you can log the token refresh
#             pass
#         else:
#             # Handle the case where the refresh token is expired or invalid
#             # You can customize the error response here
#             response.data = {
#                 "error": "Refresh token has expired or is invalid."
#             }
#
#         return response


class ManagerRegisterApi(mixins.CreateModelMixin,
                         generics.GenericAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = serializers.UserSerializer

    def post(self, request, *args, **kwargs):
        user = serializers.UserSerializer(data=request.data)
        user.is_valid(raise_exception=True)
        user.save(role='2')

        return Response({'data': user.data})


class LoginApi(mixins.CreateModelMixin,
               generics.GenericAPIView):

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'please add email or password'})

        user = authenticate(email=email, password=password)
        if user is not None:
            if user.is_active:
                # if user.role.id == 3:
                #     user_data = serializers.StudentLoginSerializer(user.student, many=False,
                #                                                    context={'request': request})
                # else:
                #     user_data = serializers.UserSerializer(user, many=False)

                refresh = RefreshToken.for_user(user)
                data = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    # 'user': user_data.data
                }
                # return Response({'data': data})
                print('got error')
                return Response(data)
            return Response({'user': 'user not active'}, status=status.HTTP_400_BAD_REQUEST)
            # {
            #                     'message': 'not verified',
            #                     'verify_status': user.verify_status,
            #                     'user': user.id,
            #                     'email': user.email
        return Response({'error': 'user_not_found'}, status=status.HTTP_400_BAD_REQUEST)


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


class GroupApi(mixins.ListModelMixin,
               mixins.CreateModelMixin,
               mixins.UpdateModelMixin,
               mixins.DestroyModelMixin,
               viewsets.GenericViewSet):
    queryset = Group.objects.select_related('faculty')
    serializer_class = serializers.GroupSerializer

    @action(methods=['get'], detail=False)
    def total(self, request, *args, **kwargs):
        group = Group.objects.annotate(
            booking_count=Count('student__booking'),
            student_count=Count('student'),
        )
        totals = group.aggregate(book_total=Sum('booking_count'), student_total=Sum('student_count'))
        serial = serializers.GroupCounterSerializer(group, many=True)
        return Response({'data': serial.data, 'totals': {'book_total': totals['book_total'],
                                                         'student_total': totals['student_total']}})


class CompanyApi(mixins.ListModelMixin,
                 mixins.CreateModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 viewsets.GenericViewSet):
    queryset = Company.objects.all()
    serializer_class = serializers.CompanySerializer

    @action(methods=['get'], detail=False)
    def total(self, request, *args, **kwargs):
        company = Company.objects.annotate(
            booking_count=Count('student__booking'),
            student_count=Count('student'),
        )
        totals = company.aggregate(book_total=Sum('booking_count'), student_total=Sum('student_count'))
        serial = serializers.CompanyCounterSerializer(company, many=True)
        return Response({'data': serial.data, 'totals': {'book_total': totals['book_total'],
                                                         'student_total': totals['student_total']}})


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
            return Response({'data': country.name}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError as e:
            return Response({'data': 'Из этой страны заселены студенты'}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False)
    def export(self, request, *args, **kwargs):
        # time.sleep(1)
        country = Country.objects.annotate(
            booking_count=Count('student__booking'),
            student_count=Count('student__id'),
        )
        totals = country.aggregate(book_total=Sum('booking_count'), student_total=Sum('student_count'))
        return export_to_excel.export_data(country, totals, 'country')


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
            booking_count=Count('group__student__booking'),
            student_count=Count('group__student'),
        )
        totals = faculty.aggregate(book_total=Sum('booking_count'), student_total=Sum('student_count'))
        serial = serializers.FacultyCounterSerializer(faculty, many=True)
        return Response({'data': serial.data, 'totals': {'book_total': totals['book_total'],
                                                         'student_total': totals['student_total']}})

    @action(methods=['get'], detail=False)
    def export(self, request, *args, **kwargs):
        faculty = Faculty.objects.annotate(
            booking_count=Count('student__booking'),
            student_count=Count('student__id'),
        )
        totals = faculty.aggregate(book_total=Sum('booking_count'), student_total=Sum('student_count'))
        return export_to_excel.export_data(faculty, totals, 'faculty')

    def destroy(self, request, *args, **kwargs):
        item_id = kwargs.get('pk')
        try:
            faculty = get_object_or_404(Faculty, pk=item_id)
            faculty.delete()
            return Response({'data': faculty.name}, status=status.HTTP_204_NO_CONTENT)
        except ProtectedError as e:
            return Response({'data': f'Из этого факультета заселены студенты'}, status=status.HTTP_400_BAD_REQUEST)


class BuildingView(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = Building.objects.select_related('principal')
    serializer_class = serializers.BuildingSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        build_id = kwargs.get('pk')
        build = get_object_or_404(Building, pk=build_id)
        serial = serializers.BuildingEditSerializer(build, request.data, partial=True)
        serial.is_valid(raise_exception=True)
        serial.save()
        return Response({'data': serial.data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        build_id = kwargs.get('pk')
        try:
            building = get_object_or_404(Building, pk=build_id)
            building.delete()
            return Response({'data': building.name, 'status': 'success'}, status=status.HTTP_200_OK)
        except ProtectedError as e:
            return Response({'data': 'В этом здание есть комнаты'}, status=status.HTTP_400_BAD_REQUEST)


class RoomTypeView(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    queryset = RoomType.objects.all()
    serializer_class = serializers.RoomTypeSerializer
    # permission_classes = (IsAuthenticated,)


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
        room = get_object_or_404(Room, pk=room_id)
        try:
            room.delete()
            return Response({'data': room.number})
        except ProtectedError as e:
            return Response({'error': f'В {room.number} комнате заселены студенты'}, status=status.HTTP_400_BAD_REQUEST)


class StudentView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Student.objects.order_by('-id')
    # serializer_class = serializers.StudentSerializer
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = StudentFilter

    def get_serializer_class(self):
        if self.action in ['list', 'create']:
            return serializers.StudentSerializer
        elif self.action in ['update', 'partial_update']:
            return serializers.StudentEditSerializer
        else:
            return super().get_serializer_class()

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

    # def update(self, request, *args, **kwargs):
    #
    #     return Response({'message': 'Ok'})

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
    permission_classes = (IsAuthenticated,)

    # parser_classes = (FormParser, MultiPartParser)

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        return Booking.objects.select_related('room__building', 'student__country', 'student__group',
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

    def create(self, request, *args, **kwargs):
        book = serializers.BookSerializer(data=request.data)
        book.is_valid(raise_exception=True)
        book_data = BookingService.add_student(book.validated_data, self.request.user.id)
        # serial = serializers.BookSerializer(book_data)
        serial = serializers.FreeAddPlaceSerializer(book_data)
        return Response({'data': serial.data})

    @action(methods=['get'], detail=False)
    def room_place(self, request, *args, **kwargs):
        room_id = request.query_params.get('id')
        book = Booking.objects.filter(room_id=room_id, status=1)
        serial = serializers.BookSerializer(book, many=True)
        return Response({'data': serial.data})

    def update(self, request, *args, **kwargs):
        start_date = datetime(2023, 10, 1).date()
        # end_date = datetime(2024, 6, 30)
        book_id = kwargs.get('pk')
        book = get_object_or_404(Booking, pk=book_id)
        book_end = datetime.strptime(request.data.get('book_end'), "%Y-%m-%d").date()

        current_date = start_date
        total_31 = 0
        feb_add_day = 0
        feb_last_day = 0
        finish_end = None
        if book_end.day == 31:
            finish_end = book_end - timedelta(1)
        else:
            finish_end = book_end

        print(finish_end, 'finish')
        while current_date <= finish_end:
            if current_date.day == 31:
                total_31 += 1
            current_date += timedelta(days=1)
            if current_date.month == 2:

                next_month = (current_date.month % 12) + 1
                feb_last_day = (datetime(current_date.year, next_month, 1) - timedelta(days=1)).day
                # feb_add_day = 30 - feb_last_day

        # print(feb_last_day in [28, 29])
        # print(end_date, 'end date')
        if feb_last_day in [28, 29]:
            feb_add_day = 30 - feb_last_day

        # book_end = request.data.get('book_end')
        # book_start = datetime.strptime(book_end, "%Y-%m-%d").date()
        # total_days = (book_start - book.book_date).days
        total_days = (finish_end - start_date).days
        print(total_days, 'days')
        if book.student.student_type_id == 1:
            # day_price = (total_days + 1 + feb_add_day) * book.student.student_type.day - total_31 * book.student.student_type.day
            day_price = (total_days + 1 + feb_add_day) * book.student.student_type.day - total_31 * book.student.student_type.day
        else:
            day_price = total_days * book.student.student_type.day

        print(day_price)

        return Response({'message': 'OK'})


class PrivilegeView(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    queryset = Privilege.objects.all()
    serializer_class = serializers.PrivilegeSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        privilege = self.get_serializer(data=request.data)
        privilege.is_valid(raise_exception=True)
        privilege.save()
        headers = self.get_success_headers(privilege.data)
        # print(headers, 'headers')
        # print(headers.keys())
        return Response({'data': privilege.data, 'headers': headers})

    def destroy(self, request, *args, **kwargs):
        privilege_id = kwargs.get('pk')
        privilege = get_object_or_404(Privilege, pk=privilege_id)
        try:
            privilege.delete()
            return Response({'data': privilege.name})
        except ProtectedError as e:
            return Response({'error': f'Это привилегия уже используется'}, status=status.HTTP_400_BAD_REQUEST)


class FreePlaceApi(mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = Room.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = FreeRoomFilter
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.FreePlaceSerializer
    pagination_class = CustomPagination

    def list(self, request, *args, **kwargs):
        free = Room.objects.select_related('building').annotate(
            free_place=F('room_type__place') - F('person_count')
        ).values('id', 'number', 'building__name', 'building_id', 'is_full', 'floor', 'room_type__place',
                 'person_count', 'free_place', 'room_gender').order_by('building_id', 'number', 'is_full')
        query = self.filter_queryset(free)
        page = self.paginate_queryset(query)
        if page is not None:
            serializer = serializers.FreePlaceSerializer(page, many=True)
            result = self.get_paginated_response(serializer.data)
            data = result.data  # pagination data
        else:
            serializer = self.get_serializer(query, many=True)
            data = serializer.data
        # build_serial = serializers.BuildingSimpleSerializer(Building.objects.all(), many=True)
        # data['results'].append({'building': build_serial.data})
        # data['building'] = build_serial.data
        return Response(data)

    @action(methods=['get'], detail=False)
    def find_student(self, request):
        query = request.query_params.get('search')

        if query is not None and query != '':
            students = Student.objects.annotate(
                has_booking=Exists(Booking.objects.filter(student_id=OuterRef('pk')))
            ).filter(has_booking=False).values('id', 'name', 'last_name')
            student = students.filter(Q(name__istartswith=query) | Q(last_name__istartswith=query))[:4]
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


class MainDormitoryApi(mixins.ListModelMixin,
                       generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

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
