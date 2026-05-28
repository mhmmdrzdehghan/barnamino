from rest_framework import serializers
from Account.models import User , StudentProfile , MentorProfile , SupportProfile
from School.models import StudentSupport
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import transaction
from django.contrib.auth import authenticate
from ChatBotAi.models import Conversation 


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model     = User
        fields    = ['id','email' , 'phone' , 'role' , 'password']
        read_only_fields = ['id']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("کاربری با این ایمیل قبلاً ثبت‌ نام کرده است.")
        return value 

    def validate_phone(self, value):
        if not value.startswith("09"):
            raise serializers.ValidationError("Phone number must start with 09.")

        if len(value) != 11:
            raise serializers.ValidationError("Phone number must be 11 digits.")

        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")

        return value
       

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        if user.role == "student":
            StudentProfile.objects.create(user=user)

        else:
            MentorProfile.objects.create(user=user)

        return user            
    
class CreatestudentSrializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True)
    class Meta:
        model = StudentProfile
        fields = [ 'id','user' , 'phone', 'first_name' , 'last_name' , 'grade',  'gender' ,'name_of_school' , 'avatar' ,'field_of_study' , 'created_at' , 'updated_at']
        read_only_fields = ['id' ,'user' , 'created_at' , 'updated_at']


    def validate_phone(self, value):
        if not value.startswith("09"):
            raise serializers.ValidationError("Phone number must start with 09.")

        if len(value) != 11:
            raise serializers.ValidationError("Phone number must be 11 digits.")

        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")

        return value
    

    def create(self, validated_data):

        with transaction.atomic():

            phone    = validated_data.pop('phone')

            user = User.objects.create(phone=phone , role='student')
            user.set_unusable_password()
            user.save()

            profile = StudentProfile.objects.create(user=user , **validated_data)

            return profile

class CreateSupportSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(write_only=True)

    class Meta:
        model = SupportProfile
        fields =['id', 'user','phone','first_name' , 'last_name' , 'is_active' , 'avatar']
        read_only_fields =['id' ,'user']


    def validate_phone(self, value):
        if not value.startswith("09"):
            raise serializers.ValidationError("Phone number must start with 09.")

        if len(value) != 11:
            raise serializers.ValidationError("Phone number must be 11 digits.")

        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")

        return value
    

    def create(self, validated_data):

        with transaction.atomic():

            phone = validated_data.pop('phone')

            user = User.objects.create(phone=phone , role='support')
            user.set_unusable_password()
            user.save()

            profile = SupportProfile.objects.create(user=user , **validated_data)

            return profile

class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    token = serializers.CharField(read_only=True)

    def validate(self, attrs):
        username = attrs.get('email')
        password = attrs.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.', code='authorization')
        else:
            raise serializers.ValidationError('Must include "username" and "password".', code='authorization')

        attrs['user'] = user
        return attrs

class MentorProfileSerializer(serializers.ModelSerializer):
    totalSuppurt = serializers.SerializerMethodField()
    totalStudent = serializers.SerializerMethodField()
    role         = serializers.SerializerMethodField() 


    class Meta:
        model = MentorProfile
        fields = [
            'id','user','first_name','last_name','avatar',
            'gender','education_level','created_at','updated_at',
            'totalSuppurt','totalStudent' , 'role'
        ]

    def get_totalSuppurt(self, obj):
        return self.context.get("totalSuppurt", 0)

    def get_totalStudent(self, obj):
        return self.context.get("totalStudent", 0)
    
    def get_role(self, instance):
        return self.context.get("role", 0)
        
class SupportProfileSerializer(serializers.ModelSerializer):
    totalStudent = serializers.SerializerMethodField()
    role         = serializers.SerializerMethodField() 
    students     = serializers.SerializerMethodField()
    phone        = serializers.SerializerMethodField()
    class Meta:
        model = SupportProfile
        fields = ['id','user','first_name','last_name', 'phone' ,'role','is_active', 'students','totalStudent' ,'avatar','created_at','updated_at']
        read_only_fields = ['id' , 'user','created_at','updated_at']

    def get_totalStudent(self , obj):

        return  StudentSupport.objects.filter(support = obj.user).count()
    
    def get_role(self, obj):
        return "support"
    
    def get_students(self, obj):
        return StudentSupport.objects.filter(support=obj.user).values_list("student" , flat=True)
    
    def get_phone(self, obj):
        return obj.user.phone
    
       
class StudentProfileSerializer(serializers.ModelSerializer):
    role         = serializers.SerializerMethodField() 
    conversation = serializers.SerializerMethodField()
    class Meta:
        model = StudentProfile
        fields = ['id','user','first_name','last_name','role' , 'avatar', 'grade', 'conversation' ,'field_of_study', 'gender' , 'name_of_school','created_at','updated_at']
        read_only_fields = ['id' , 'user', 'conversation','created_at','updated_at']

    def validate_phone(self, value):
        if not value.startswith("09"):
            raise serializers.ValidationError("Phone number must start with 09.")

        if len(value) != 11:
            raise serializers.ValidationError("Phone number must be 11 digits.")

        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")

        return value

    def get_role(self, obj):
        return self.context.get("role", 0)
    
    def get_avatar(self, obj):
        request = self.context.get('request')
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return None
    

    
    def get_conversation(self, obj):

        return Conversation.objects.filter(created_by=obj.user).first().id
        







