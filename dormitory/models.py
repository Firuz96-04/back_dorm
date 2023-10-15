from datetime import date

from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from imagekit.models import ProcessedImageField
from .utils import main_util
# Create your models here.
from ant_back import settings


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class Role(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'role'


class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLES = [
        ('1', 'admin'),
        ('2', 'manager'),
        ('3', 'commandant')
    ]

    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    phone = models.CharField(max_length=14, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    role = models.CharField(choices=ROLES, max_length=1)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    objects = CustomUserManager()

    def __str__(self):
        return str(self.email)

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return self.is_staff

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Company(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=40)
    phone = models.CharField(max_length=15, blank=True)
    director = models.CharField(max_length=40, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'company'


class Country(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=40)

    class Meta:
        db_table = 'country'

    def __str__(self):
        return self.name


class Principal(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=25, blank=True)
    last_name = models.CharField(max_length=25, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'principal'


class Faculty(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'faculty'


class Group(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=40)
    faculty = models.ForeignKey(Faculty, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'group'


class Building(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=25, blank=True)
    address = models.CharField(max_length=100, blank=True)
    principal = models.ForeignKey(Principal, on_delete=models.CASCADE, related_name='buildings', blank=True, null=True)
    floor_count = models.SmallIntegerField(default=5)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'building'


class StudentType(models.Model):
    TYPE = [
        ('foreigner', 'иностранец'),
        ('local', 'местный'),
    ]
    id = models.SmallAutoField(primary_key=True)
    type = models.CharField(max_length=15, choices=TYPE)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    day = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        db_table = 'student_type'


class BookingStatus(models.Model):
    CHOICES = (
        (1, 'booking'),
        (2, 'process'),
        (3, 'canceling'),
    )

    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=20, choices=CHOICES)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'booking_status'


class RoomType(models.Model):
    id = models.SmallAutoField(primary_key=True)
    place = models.PositiveSmallIntegerField(default=True)

    def __str__(self):
        return f'{self.place}'

    class Meta:
        db_table = 'room_type'


class Room(models.Model):
    ROOM_GENDER = (
        ('0', 'женшина'),
        ('1', 'мужчина'),
        ('2', 'пусто'),
    )

    id = models.SmallAutoField(primary_key=True)
    number = models.CharField(max_length=4)
    floor = models.PositiveSmallIntegerField()
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
    is_full = models.BooleanField(default=False)
    building = models.ForeignKey(Building, on_delete=models.PROTECT)
    description = models.CharField(max_length=128, blank=True)
    person_count = models.SmallIntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room_gender = models.CharField(max_length=1, choices=ROOM_GENDER, default='2')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.number} {self.building.name}'

    class Meta:
        db_table = 'room'


class Student(models.Model):
    GENDER_CHOICE = (
        ('0', 'женшина'),
        ('1', 'мужчина'),
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    born = models.DateField()
    course = models.CharField(max_length=1, default=1)
    address = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICE)
    photo = ProcessedImageField(upload_to=main_util.upload_photo, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT)
    nationality = models.CharField(max_length=20, blank=True)
    student_type = models.ForeignKey(StudentType, on_delete=models.PROTECT)
    group = models.ForeignKey(Group, on_delete=models.PROTECT)
    company = models.ForeignKey(Company, on_delete=models.PROTECT, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} {self.last_name}'

    class Meta:
        db_table = 'student'


class Privilege(models.Model):
    id = models.SmallAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=125, blank=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        db_table = 'privilege'


def curr_date():
    return date.today()


class Booking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    book_date = models.DateField(default=curr_date)
    book_end = models.DateField(default=curr_date)
    privilege = models.ForeignKey(Privilege, on_delete=models.PROTECT, blank=True, null=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    status = models.ForeignKey(BookingStatus, on_delete=models.PROTECT, default=1)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        db_table = 'booking'


class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    bill = models.CharField(max_length=20, blank=True)
    comment = models.TextField(blank=True)
    payed_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payment'


class TestBooking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    book_start = models.DateField(default=curr_date)
    book_end = models.DateField()
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    privilege = models.ForeignKey(Privilege, on_delete=models.PROTECT)

    # created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'test_book'


