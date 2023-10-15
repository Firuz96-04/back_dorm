from django.urls import path
from .views import (CountryView, PrincipalView,
                    FacultyView, BuildingView, RoomTypeView, StudentView, RoomView,
                    PrivilegeView, BookView, FreePlaceApi, ManagerRegisterApi, StudentTypeApi, CompanyApi, GroupApi,
                    CatApi, MainDormitoryApi)
from rest_framework.routers import DefaultRouter
from accounts.views import PaymentApi

router = DefaultRouter(trailing_slash=False)
router.register(r'country', CountryView, basename='country')
router.register(r'principal', PrincipalView, basename='principal')
router.register(r'faculty', FacultyView, basename='faculty')
router.register(r'building', BuildingView, basename='building')
router.register(r'room-type', RoomTypeView, basename='room_type')
router.register(r'room', RoomView, basename='room')
router.register(r'student', StudentView, basename='student')
router.register(r'booking', BookView, basename='booking')
router.register(r'free-place', FreePlaceApi, basename='free-place')
router.register(r'student-type', StudentTypeApi, basename='student-type')
router.register(r'privilege', PrivilegeView, basename='privilege')

router.register(r'company', CompanyApi, basename='company')
router.register(r'group', GroupApi, basename='group')
# account

router.register(r'payment', PaymentApi, basename='payment')



urlpatterns = [
    # path('country', CountryView.as_view())
    path('user-register', ManagerRegisterApi.as_view()),
    path('category', CatApi.as_view()),
    path('main-dorm', MainDormitoryApi.as_view())
]

urlpatterns += router.urls
