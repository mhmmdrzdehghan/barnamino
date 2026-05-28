from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Role(models.TextChoices):
    STUDENT = "student", "Student"
    MENTOR = "mentor", "Mentor"
    SUPPORT = "support", "Support"



class FieldOfStudy(models.TextChoices):
    MATH = "math", "ریاضی"
    EXPERIMENTAL = "experimental", "تجربی"
    HUMANITIES = "humanities", "انسانی"


class Gedner(models.TextChoices):
    MALE = "male", "مرد"
    FEMALE = "female", "زن"

class Grade(models.TextChoices):
    TENTH = "10", "پایه دهم"
    ELEVENTH = "11", "پایه یازدهم"
    TWELFTH = "12", "پایه دوازدهم"

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email باید وارد شود') 
        email = self.normalize_email(email)
        user = self.model(email=email,  **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email , password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)

    role = models.CharField(max_length=20, choices=Role.choices)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email or self.phone

class StudentProfile(models.Model):
    user              = models.OneToOneField(User , related_name='Student_Profile' , on_delete=models.CASCADE)
    # mentor            = models.ForeignKey(User , related_name='StudentProfile' , blank=True , null=True , on_delete=models.CASCADE)
    # supports          = models.ManyToManyField(User , related_name='students')
    first_name        = models.CharField( max_length=255)
    last_name         = models.CharField( max_length=255)
    grade             = models.CharField( max_length=50 , choices=Grade.choices)
    gender            = models.CharField(max_length=255 , choices=Gedner.choices)
    field_of_study    = models.CharField(max_length=50 , choices=FieldOfStudy.choices)
    name_of_school    = models.CharField(max_length=250)

    avatar            = models.ImageField(upload_to="avatars/student/",null=True,blank=True)

    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

class MentorProfile(models.Model):
    user              = models.OneToOneField(User , related_name='MentorProfile' , on_delete=models.CASCADE)
    first_name        = models.CharField( max_length=255)
    last_name         = models.CharField( max_length=255)
    gender            = models.CharField(max_length=255 , choices=Gedner.choices)
    education_level   = models.CharField(max_length=255)

    avatar            = models.ImageField(upload_to="avatars/mentors/",null=True,blank=True)

    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

class SupportProfile(models.Model):
    user              = models.OneToOneField(User,on_delete=models.CASCADE, related_name="support_profile")
    first_name        = models.CharField(max_length=255)
    last_name         = models.CharField(max_length=255)
    is_active         = models.BooleanField(default=True)
    avatar            = models.ImageField(upload_to="avatars/Support/",null=True,blank=True)

    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

