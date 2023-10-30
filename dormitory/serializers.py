from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, status
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.exceptions import APIException, ValidationError
from .models import (Country, Faculty, Building,
                     RoomType, Student, Room, Privilege, Booking, CustomUser, Company, Group, StudentType)

from .validators import (validate_building, validate_room, validate_faculty, common_validate, validate_city_country,
                         validate_register)
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.exceptions import AuthenticationFailed
from datetime import date


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        # validated_data = super().validate(attrs)
        try:
            validated_data = super().validate(attrs)
        except Exception as e:
            raise AuthenticationFailed({'error': 'refresh_expired', 'status': '401'})
        # except TokenError as e:
        #     raise AuthenticationFailed({'error': 'refresh_expired', 'status': '401'})

        # Add custom logic here if needed
        user = self.context['request'].user  # Get the current user from the request

        # For example, you can check if the user is active
        # if not user.is_active:
        #     raise serializers.ValidationError("User is not active.")

        # You can also check for other conditions, such as user roles or permissions
        # if not user.has_permission('some_permission'):
        #     raise serializers.ValidationError("User does not have the required permission.")

        # If all custom checks pass, return the validated data
        return validated_data


class CustomUserSerializer(serializers.Serializer):
    name = serializers.CharField(source='first_name')
    last_name = serializers.CharField()
    role = serializers.SerializerMethodField(method_name='get_role')

    def get_role(self, obj):
        role = ''
        if obj.role == '1':
            role = 'admin'
        elif obj.role == '2':
            role = 'accountant'

        return role


class CommandantUserSerializer(serializers.Serializer):
    name = serializers.CharField(source='first_name')
    last_name = serializers.CharField()
    role = serializers.SerializerMethodField(method_name='get_role')
    # building_name = serializers.CharField(source='commandant.building.name', read_only=True)
    # building_id = serializers.CharField(source='commandant.building.id', read_only=True)
    building = serializers.SerializerMethodField()

    def get_building(self, obj):
        building = obj.commandant.building
        if building is None:
            return None
        else:
            return {
                'building_name': building.name,
                'building_id': building.id,
                'building_floor': building.floor_count,

            }

    def get_role(self, obj):
        role = ''
        if obj.role == '3':
            role = 'commandant'

        return role


class UserSerializer(ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    # role = serializers.CharField(read_only=True)

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
        print(validated_data, 'data')
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
            raise APIException({'error': errors[0]})
        return data


class FacultySerializer(ModelSerializer):
    class Meta:
        model = Faculty
        fields = ('id', 'name')

    def validate(self, data):
        errors = validate_faculty(data)
        if errors:
            raise APIException({'error': errors[0]})
        return data


class FacultyEditSerializer(ModelSerializer):
    class Meta:
        model = Faculty
        fields = ('id', 'name')

    def validate(self, data):
        faculty = Faculty.objects.filter(name=data['name'])
        is_exist = faculty[0].name == data['name']
        if is_exist:
            raise APIException({'error': 'this faculty exists'})
        return data


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

    def validate(self, data):
        group = Group.objects.filter(name=data['name'], faculty=data['faculty'])
        if group:
            raise APIException({'error': 'this group exists'})
        return data

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['faculty'] = FacultySerializer(instance.faculty).data

        return response


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

    def validate(self, data):
        return common_validate(Company, data, 'company')
        # company = Company.objects.filter(name__iexact=data['name'])
        # if company:
        #     raise APIException({'company': f'{data["name"]} уже добавлено'})
        # return data


class CountryCounterSerializer(Serializer):
    student_count = serializers.IntegerField()
    booking_count = serializers.IntegerField()
    name = serializers.CharField()
    id = serializers.IntegerField()


class FacultyCounterSerializer(Serializer):
    student_count = serializers.IntegerField()
    booking_count = serializers.IntegerField()
    name = serializers.CharField()
    id = serializers.IntegerField()


class CompanyCounterSerializer(Serializer):
    student_count = serializers.IntegerField()
    booking_count = serializers.IntegerField()
    name = serializers.CharField()
    phone = serializers.CharField()
    director = serializers.CharField()
    description = serializers.CharField()
    id = serializers.IntegerField()


class GroupCounterSerializer(Serializer):
    student_count = serializers.IntegerField()
    booking_count = serializers.IntegerField()
    name = serializers.CharField()
    faculty = serializers.CharField(source='faculty.name')
    faculty_id = serializers.IntegerField(source='faculty.id')
    id = serializers.IntegerField()


class OnlyGroupSerializer(ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class OnlyCompanySerializer(Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class BuildingSerializer(ModelSerializer):
    class Meta:
        model = Building
        fields = ('id', 'name', 'address', 'floor_count', 'description')

    def validate(self, data):
        errors = validate_building(data)
        if errors:
            raise APIException({'error': errors[0]})
        return data

    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     return response


class BuildingEditSerializer(ModelSerializer):
    class Meta:
        model = Building
        fields = ('id', 'name', 'address', 'floor_count', 'description')

    def validate(self, data):
        name = data.get('name')
        if name is not None:
            building = Building.objects.filter(name__icontains=name)
            if building:
                raise APIException({'building': f'{name} уже добавлено'})
        return data

    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     return response


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
    room_gender = serializers.CharField()


class BookStudentSerializer(Serializer):
    id = serializers.IntegerField()
    full_name = serializers.SerializerMethodField(method_name='get_full_name')
    course = serializers.CharField(max_length=1)
    student_type = serializers.CharField(source='student_type.type')
    group = OnlyGroupSerializer()
    country = CountrySerializer()
    gender = serializers.CharField(max_length=1)

    def get_full_name(self, obj):
        return f'{obj.name} {obj.last_name} {obj.sure_name}'


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
            raise APIException({'error': f"{data['number']} комната уже добавлено"})
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
        fields = ('id', 'name', 'last_name', 'sure_name', 'country', 'phone', 'born', 'address',
                  'gender', 'company', 'student_type', 'group', 'course', 'user', 'created_at')

    def validate(self, data):
        errors = []
        student = Student.objects.filter(name__iexact=data['name'], last_name__iexact=data['last_name'])
        if student:
            errors.append({'student': 'this student uje v baze'})

        if errors:
            raise APIException({'student': errors})
        return data

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['country'] = CountrySerializer(instance.country).data
        response['group'] = OnlyGroupSerializer(instance.group).data
        if response['company'] is not None:
            response['company'] = OnlyCompanySerializer(instance.company).data
        else:
            response['company'] = None
        response['student_type'] = StudentTypeSerializer(instance.student_type).data

        return response


class StudentEditSerializer(ModelSerializer):
    user = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M', read_only=True)

    class Meta:
        model = Student
        fields = ('id', 'name', 'last_name', 'sure_name', 'country', 'phone', 'born', 'address',
                  'gender', 'company', 'student_type', 'group', 'course', 'user', 'created_at')

    def validate(self, data):
        errors = []
        student = Student.objects.filter(name__iexact=data.get('name'), last_name__iexact=data.get('last_name'))
        if student:
            errors.append({'student': 'this student uje v baze'})

        if errors:
            raise APIException({'student': errors})
        return data

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['country'] = CountrySerializer(instance.country).data
        response['group'] = OnlyGroupSerializer(instance.group).data
        response['student_type'] = StudentTypeSerializer(instance.student_type).data
        if response['company'] is not None:
            response['company'] = OnlyCompanySerializer(instance.company).data
        else:
            response['company'] = None
        # response['company'] = OnlyCompanySerializer(instance.company).data

        return response


class BookSerializer(ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", required=False)
    user = serializers.CharField(read_only=True, required=False)
    debt = serializers.SerializerMethodField(method_name='get_debt')
    day_lives = serializers.SerializerMethodField(method_name='get_day_lives')

    class Meta:
        model = Booking
        fields = ('id', 'student', 'room', 'privilege', 'user', 'total_price',
                  'payed', 'debt', 'book_date', 'book_end', 'status', 'day_lives', 'created_at')

    def get_debt(self, obj):
        total_debt = obj.total_price - obj.payed
        return str(total_debt)

    def get_day_lives(self, obj):
        today = date.today()
        total = today - obj.book_date
        return total.days

    def validate(self, data):
        errors = []
        book = Booking.objects.filter(student=data['student'])

        if book:
            errors.append({'student': 'Этот студент уже заселен'})

        if data['room'].room_gender == '2':
            pass
        else:
            if data['room'].room_gender != data['student'].gender:
                if data['room'].room_gender == '0':
                    raise APIException({'gender': 'Вы можете заселить только женщин'})
                else:
                    raise APIException({'gender': 'Вы можете заселить только мужчин'})
            else:
                pass

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
            errors.append('Это привилегия уже добавлено')

        if errors:
            raise APIException({'error': errors[0]})
        return data


class ContractSerializer(ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", required=False)
    user = serializers.CharField(read_only=True, required=False)
    debt = serializers.SerializerMethodField(method_name='get_debt')
    day_lives = serializers.SerializerMethodField(method_name='get_day_lives')

    class Meta:
        model = Booking
        fields = ('id', 'student', 'room', 'privilege', 'user', 'total_price',
                  'payed', 'debt', 'book_date', 'book_end', 'status', 'day_lives', 'created_at')

    def get_debt(self, obj):
        total_debt = obj.total_price - obj.payed
        return str(total_debt)

    def get_day_lives(self, obj):
        # today = date.today()
        total = obj.book_end - obj.book_date
        return total.days

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['room'] = BookRoomSerializer(instance.room).data
        response['student'] = BookStudentSerializer(instance.student).data
        return response


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
    room_gender = serializers.CharField()


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
    room_gender = serializers.CharField()

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


class FreeRoomSerializer(Serializer):
    room_id = serializers.IntegerField(source='id')
    number = serializers.CharField()
    person_count = serializers.IntegerField()
    room_gender = serializers.SerializerMethodField()

    def get_room_gender(self, obj):
        gender = obj['room_gender']
        if gender == '0':
            return 'женское'
        elif gender == '1':
            return 'мужское'
        else:
            return 'пусто'
