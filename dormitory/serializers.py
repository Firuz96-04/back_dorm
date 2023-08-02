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


class BookStudentSerializer(Serializer):
    id = serializers.IntegerField()
    full_name = serializers.SerializerMethodField(method_name='get_full_name')
    faculty = FacultySerializer()
    country = CountrySerializer()

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
        errors = []
        room = Room.objects.filter(number=data['number'], building_id=data['building'])
        if room:
            errors.append({'room': 'this room exist'})
        if errors:
            raise ValidationError({'errors': errors})
        return data

    def to_representation(self, instance):
        building = BuildingSimpleSerializer(instance.building).data
        response = super().to_representation(instance)

        response['room_type'] = RoomTypeSerializer(instance.room_type).data
        response['building_name'] = building['name']
        response['building_floor_count'] = building['floor_count']

        # response['building_'] = BuildingSimpleSerializer(instance.building).data

        return response


class StudentTypeSerializer(ModelSerializer):
    class Meta:
        model = StudentType
        fields = '__all__'


class StudentSerializer(ModelSerializer):
    user = serializers.CharField(read_only=True)

    # born_n = serializers.DateField(format='%Y-%m-%d')

    class Meta:
        model = Student
        fields = ('id', 'name', 'last_name', 'country', 'phone', 'born', 'address',
                  'gender', 'student_type', 'faculty', 'course', 'user')

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
    created_at = serializers.DateTimeField(format="%d.%m.%Y", required=False)
    user = serializers.CharField(read_only=True)

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
        response = super(BookSerializer, self).to_representation(instance)
        response['room'] = BookRoomSerializer(instance.room).data
        response['student'] = BookStudentSerializer(instance.student).data
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
