from django.urls import path
from .views import (CountryView, PrincipalView,
                    FacultyView, BuildingView, RoomTypeView, StudentView, RoomView,
                    PrivilegeView, BookView, ManagerRegisterApi)
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r'country', CountryView, basename='country')
router.register(r'principal', PrincipalView, basename='principal')
router.register(r'faculty', FacultyView, basename='faculty')
router.register(r'building', BuildingView, basename='building')
router.register(r'room-type', RoomTypeView, basename='room_type')
router.register(r'room', RoomView, basename='room')
router.register(r'student', StudentView, basename='student')
router.register(r'booking', BookView, basename='booking')

router.register(r'privilege', PrivilegeView, basename='privilege')


urlpatterns = [
    # path('country', CountryView.as_view())
    path('user-register', ManagerRegisterApi.as_view())
]

urlpatterns += router.urls
