from abc import ABC

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.exceptions import APIException, ValidationError
from .models import (Country, Principal, Faculty, Building,
                     RoomType, Student, Room, Privilege, Booking, CustomUser, StudentType)

from .validators import (validate_building, validate_room, validate_faculty, validate_principal, validate_city_country,
                         validate_register)


class UserSerializer(ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'role',
                  'phone', 'password', 'password2')

    def validate(self, data):
        errors = validate_register(data)
        if errors:
            raise ValidationError({'errors': errors})
        return data

    def create(self, validated_data):
        print(validated_data)
        user = CustomUser.objects.create(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            role=validated_data['role'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class CountrySerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name')

    def validate(self, data):
        errors = validate_city_country(data, Country)
        if errors:
            raise ValidationError({'errors': errors})
        return data


class CountryCounterSerializer(Serializer):
    student_count = serializers.IntegerField()
    booking_count = serializers.IntegerField()
    name = serializers.CharField()
    id = serializers.IntegerField()


class PrincipalSerializer(ModelSerializer):
    class Meta:
        model = Principal
        fields = ('id', 'name', 'last_name', 'phone', 'address')

    def validate(self, data):
        errors = validate_principal(data)
        if errors:
            raise ValidationError({'errors': errors})
        return data


class FacultySerializer(ModelSerializer):
    class Meta:
        model = Faculty
        fields = ('id', 'name')

    def validate(self, data):
        errors = validate_faculty(data)
        if errors:
            raise ValidationError({'errors': errors})
        return data


class FacultyCounterSerializer(Serializer):
    student_count = serializers.IntegerField()
    booking_count = serializers.IntegerField()
    name = serializers.CharField()
    id = serializers.IntegerField()


class BuildingSerializer(ModelSerializer):
    class Meta:
        model = Building
        fields = ('id', 'name', 'address', 'principal', 'floor_count', 'description')

    def validate(self, data):
        errors = validate_building(data)
        if errors:
            raise APIException({'errors': errors})
        return data

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['principal'] = PrincipalSerializer(instance.principal).data

        return response


class BuildingSimpleSerializer(Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    floor_count = serializers.IntegerField()


class BookRoomSerializer(Serializer):
    id = serializers.IntegerField()
    number = serializers.CharField()
    floor = serializers.IntegerField()
    building = serializers.CharField(source='building.name')
    building_id = serializers.IntegerField(source='building.id')


class BookStudentSerializer(Serializer):
    id = serializers.IntegerField()
    full_name = serializers.SerializerMethodField(method_name='get_full_name')
    course = serializers.CharField(max_length=1)
    faculty = FacultySerializer()
    country = CountrySerializer()
    gender = serializers.CharField(max_length=1)

    def get_full_name(self, obj):
        return f'{obj.name} {obj.last_name}'


class RoomTypeSerializer(ModelSerializer):
    class Meta:
        model = RoomType
        fields = ('id', 'place')

    def validate(self, data):
        errors = validate_room(data)
        if errors:
            raise APIException({'errors': errors})
        return data


class RoomSerializer(ModelSerializer):
    user = serializers.CharField(read_only=True)

    class Meta:
        model = Room
        fields = ('id', 'number', 'floor', 'room_type', 'building',
                  'is_full', 'user', 'description')

    def validate(self, data):
        room = Room.objects.filter(number=data['number'], building_id=data['building'])
        if room:
            raise APIException({'room': 'this room is exists'})
        return data

    def to_representation(self, instance):
        building = BuildingSimpleSerializer(instance.building).data
        response = super().to_representation(instance)
        response['room_type'] = RoomTypeSerializer(instance.room_type).data
        response['building_name'] = building['name']
        response['building_floor_count'] = building['floor_count']
        return response


class RoomEditSerializer(ModelSerializer):
    # user = serializers.CharField(read_only=True)

    class Meta:
        model = Room
        fields = ('id', 'number', 'floor', 'room_type', 'building', 'description')

    def validate(self, data):
        print(data)
        # room = Room.objects.filter(number=data['number'], building_id=data['building'])
        # if room:
        #     raise APIException({'room': 'this room is exists'})
        return data

    def to_representation(self, instance):
        building = BuildingSimpleSerializer(instance.building).data
        response = super().to_representation(instance)
        response['room_type'] = RoomTypeSerializer(instance.room_type).data
        response['building_name'] = building['name']
        response['building_floor_count'] = building['floor_count']
        return response


class StudentTypeSerializer(ModelSerializer):
    class Meta:
        model = StudentType
        fields = '__all__'


class StudentSerializer(ModelSerializer):
    user = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M', read_only=True)

    class Meta:
        model = Student
        fields = ('id', 'name', 'last_name', 'country', 'phone', 'born', 'address',
                  'gender', 'student_type', 'faculty', 'course', 'user', 'created_at')

    def validate(self, data):
        errors = []
        student = Student.objects.filter(name__iexact=data['name'], last_name__iexact=data['last_name'])
        if student:
            errors.append({'student': 'this student uje v baze'})

        if errors:
            raise APIException({'student': errors})
        return data

    def to_representation(self, instance):
        resonse = super(StudentSerializer, self).to_representation(instance)
        resonse['country'] = CountrySerializer(instance.country).data
        resonse['faculty'] = FacultySerializer(instance.faculty).data
        resonse['student_type'] = StudentTypeSerializer(instance.student_type).data

        return resonse


class BookSerializer(ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", required=False)
    user = serializers.CharField(read_only=True, required=False)
    debt = serializers.SerializerMethodField(method_name='get_debt')

    class Meta:
        model = Booking
        fields = ('student', 'room', 'privilege', 'user', 'total_price',
                  'payed', 'debt', 'book_date', 'book_end', 'created_at')

    def get_debt(self, obj):
        total_debt = obj.total_price - obj.payed
        return str(total_debt)

    def validate(self, data):
        errors = []
        book = Booking.objects.filter(student=data['student'])

        if book:
            errors.append({'student': 'student exists'})

        if errors:
            raise ValidationError({'errors': errors})
        return data

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['room'] = BookRoomSerializer(instance.room).data
        response['student'] = BookStudentSerializer(instance.student).data
        return response


class FreeBookSerializer(ModelSerializer):
    # created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", required=False)
    user = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = Booking
        fields = ('student', 'room', 'privilege', 'user', 'created_at')

    def validate(self, data):
        errors = []
        book = Booking.objects.filter(student=data['student'])

        if book:
            errors.append({'student': 'student exists'})

        if errors:
            raise ValidationError({'errors': errors})
        return data

    def to_representation(self, instance):
        response = super().to_representation(instance)
        # response['room'] = BookRoomSerializer(instance.room).data
        return response


class PrivilegeSerializer(ModelSerializer):
    class Meta:
        model = Privilege
        fields = ('id', 'name', 'description')

    def validate(self, data):
        errors = []
        privilege = Privilege.objects.filter(name__iexact=data['name'])
        if privilege:
            errors.append({'privilege': 'this privilege exists'})

        if errors:
            raise APIException({'error': errors})
        return data


class FreePlaceSerializer(Serializer):
    room_id = serializers.IntegerField(source='id')
    number = serializers.CharField()
    floor = serializers.IntegerField()
    building = serializers.CharField(source='building__name')
    building_id = serializers.IntegerField()
    is_full = serializers.BooleanField()
    room_place = serializers.IntegerField(source='room_type__place')
    person_count = serializers.IntegerField()
    free_place = serializers.IntegerField()


class FreeAddPlaceSerializer(Serializer):
    room_id = serializers.IntegerField(source='id')
    number = serializers.CharField()
    floor = serializers.IntegerField()
    building = serializers.CharField()
    building_id = serializers.IntegerField()
    is_full = serializers.BooleanField()
    room_place = serializers.IntegerField(source='room_type.place')
    person_count = serializers.IntegerField()
    free_place = serializers.SerializerMethodField(method_name='get_free_place')

    def get_free_place(self, obj):
        total = obj.room_type.place - obj.person_count
        return total


class FreeStudentSearch(Serializer):
    code = serializers.IntegerField(source="id")
    name = serializers.SerializerMethodField(method_name="get_full_name")

    def get_full_name(self, obj):
        return f'{obj["name"]} {obj["last_name"]}'


class MainDormitorySerializer(Serializer):
    total_rooms = serializers.IntegerField()
    busy_rooms = serializers.IntegerField()
    free_rooms = serializers.IntegerField()
    women = serializers.IntegerField()
    men = serializers.IntegerField()
    all_student = serializers.IntegerField()
    build_name = serializers.CharField()
    build_id = serializers.IntegerField()
    floor_size = serializers.IntegerField()

    pass