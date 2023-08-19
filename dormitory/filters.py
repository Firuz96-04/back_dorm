from django.db.models import Q
from django_filters import rest_framework as filters
from dormitory.models import Student, Room, Booking


class StudentFilter(filters.FilterSet):
    course = filters.CharFilter()
    faculty = filters.NumberFilter(field_name='faculty_id')
    country = filters.NumberFilter(field_name='country_id')
    type = filters.NumberFilter(field_name='student_type')
    search = filters.CharFilter(method='full_name')

    class Meta:
        model = Student
        fields = ('name', 'course', 'faculty', 'country', 'type')

    def full_name(self, queryset, name, value):
        return queryset.filter(Q(name__istartswith=value) | Q(last_name__istartswith=value))


class FreeRoomFilter(filters.FilterSet):
    building = filters.NumberFilter(field_name='building_id')
    is_full = filters.BooleanFilter()
    room = filters.CharFilter(field_name='number', lookup_expr='startswith')
    floor = filters.NumberFilter()
    place = filters.NumberFilter(field_name='free_place')

    class Meta:
        model = Room
        fields = ('building', 'number', 'is_full', 'floor')

    # def filter_place(self, queryset, name, value):
    #     print(value, 'value')
    #     print(name, 'name')
    #     return queryset.filter()''


class BookFilter(filters.FilterSet):
    building = filters.NumberFilter(field_name='room__building_id')
    room = filters.CharFilter(field_name='room__number', lookup_expr='startswith')
    search = filters.CharFilter(method='full_name')
    faculty = filters.NumberFilter(field_name='student__faculty_id')
    gender = filters.CharFilter(field_name='student__gender')
    privilege = filters.NumberFilter(field_name='privilege')

    class Meta:
        model = Booking
        fields = ('building', 'search', 'privilege', 'faculty', 'gender')

    def full_name(self, queryset, name, value):
        return queryset.filter(Q(student__name__istartswith=value) | Q(student__last_name__istartswith=value))
