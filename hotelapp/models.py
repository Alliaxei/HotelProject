from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.template.context_processors import request
from datetime import date

class Room(models.Model):
    room_number = models.IntegerField(unique=True, default=0)
    building = models.CharField(max_length=255)
    floor = models.IntegerField()
    bathRoomType = models.CharField(max_length=255)
    numberOfSeats = models.IntegerField()
    room_category = models.CharField(max_length=255, choices= [
        ('economy', 'Эконом'),
        ('standart', 'Стандарт'),
        ('luxury', 'Люкс'),
    ], default='economy')


    def __str__(self):
        return (f'№: {self.room_number},'
                f'Корпус: {self.building},'
                f' Этаж: {self.floor},'
                f' Тип ванной: {self.bathRoomType},'
                f' Число мест: {self.numberOfSeats}'
                f' Категория: {self.room_category}')

    def get_category_display(self):
        category_dict = dict(self._meta.get_field('room_category').choices) #Преобразование списка кортежей в словарь
        return category_dict.get(self.room_category, self.room_category) # Возвращение значения по ключу


class Client(models.Model):
    name = models.CharField(max_length=255)
    passport = models.CharField(max_length=255)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    lengthOfStay = models.IntegerField(help_text="Срок проживания в днях")
    date_of_check_in = models.DateField(default=date.today)



    def __str__(self):
        return (f'Клиент: {self.name}, '
                f'Паспорт: {self.passport}, '
                f'Номер: {self.room.room_number}, '
                f'Срок проживания: {self.lengthOfStay} дней')

class UserManager(BaseUserManager):
    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise ValueError('Поле для логина должно быть заполнено')
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(login, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []

    def __str__(self):
        return (f'Логин: {self.login}, '
                f'пароль: {self.password}, '
                f'Тип: {self.is_superuser}')

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser