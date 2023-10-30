from django.db.models import Q, F
from django_filters import rest_framework as filters
from dormitory.models import Student, Room, Booking, Group


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
    gender = filters.CharFilter(field_name='room_gender')

    class Meta:
        model = Room
        fields = ('building', 'number', 'is_full', 'floor', 'gender')

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
    privilege = filters.NumberFilter(method='get_privilege')
    debt = filters.NumberFilter(method='get_debt')

    class Meta:
        model = Booking
        fields = ('building', 'search', 'privilege', 'faculty', 'gender', 'debt')

    def full_name(self, queryset, name, value):
        return queryset.filter(Q(student__name__istartswith=value) | Q(student__last_name__istartswith=value))

    def get_debt(self, queryset, name, value):
        if value == 1:
            return queryset.filter(Q(total_price=F('payed')))
        else:
            return queryset.exclude(Q(total_price=F('payed')))

    def get_privilege(self, queryset, name, value):
        if value == 1:
            return queryset.filter(Q(privilege_id__isnull=True))
        else:
            return queryset.filter(privilege_id__isnull=False)


class RoomFilter(filters.FilterSet):
    room = filters.NumberFilter(field_name='number', lookup_expr='startswith')
    building = filters.NumberFilter()
    gender = filters.CharFilter(field_name='room_gender')

    class Meta:
        model = Room
        fields = ('room', 'building', 'gender')


class GroupFilter(filters.FilterSet):
    faculty = filters.NumberFilter()
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Group
        fields = ('name', 'faculty')