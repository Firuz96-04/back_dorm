from rest_framework.exceptions import APIException
from .models import (Building, RoomType, Faculty, CustomUser)


def common_validate(object, data, title):
    main = object.objects.filter(name__iexact=data['name'])
    if main:
        raise APIException({title: f'{data["name"]} уже добавлено'})
    return data


def validate_building(data):
    errors = []
    building = Building.objects.filter(name__iexact=data['name'])
    if building:
        errors.append(f'{data["name"]} уже добавлено')
    return errors


def validate_room(data):
    errors = []
    room_type = RoomType.objects.filter(place__iexact=data['place'])
    if room_type:
        errors.append({'place': 'exists'})

    return errors


def validate_faculty(data):
    errors = []
    faculty = Faculty.objects.filter(name__iexact=data['name'])
    if faculty:
        errors.append(f'{data["name"]} уже добавлено')
    return errors


def validate_city_country(data, object):
    errors = []
    country = object.objects.filter(name__iexact=data['name'])
    if country:
        errors.append(f'{data["name"]} уже добавлено')
    return errors


def validate_register(data):
    errors = []
    user = CustomUser.objects.filter(first_name__iexact=data['first_name'],
                                     last_name__iexact=data['last_name'])
    if data['password'] != data['password2']:
        errors.append({'password': 'no compare'})

    if CustomUser.objects.filter(email__iexact=data['email']):
        errors.append({'email': 'email has exist'})

    if user:
        errors.append({'user': 'this user already has'})

    return errors
