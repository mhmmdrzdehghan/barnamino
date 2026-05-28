from django.shortcuts import render
from rest_framework.generics import CreateAPIView , RetrieveUpdateAPIView , RetrieveAPIView , DestroyAPIView
from rest_framework.viewsets import ModelViewSet
from .serializer import UserSerializer , CreatestudentSrializer , CreateSupportSerializer , MentorProfileSerializer , CustomAuthTokenSerializer , SupportProfileSerializer , StudentProfileSerializer
from rest_framework_simplejwt.views import TokenObtainPairView  , TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from Account.permissions import IsMentor , IsStudent , IsSupport
from rest_framework.permissions import IsAuthenticated
from Account.models import StudentProfile , SupportProfile , MentorProfile , User
from School.models import StudentSupport
from drf_spectacular.utils import extend_schema, extend_schema_view , OpenApiExample
from rest_framework.views import APIView
from django.core.cache import cache
import random
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken 
from django.db import transaction
from ChatBotAi.models import Conversation


# from rest_framework.parsers import MultiPartParser, FormParser




@extend_schema(summary="ثبت نام کاربر",description="معمولا فقط مشاور برای ثبت نام از این اندپوینت استفاده میکند")       
class Register(CreateAPIView):
    serializer_class = UserSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):

        response = super().create(request, *args, **kwargs)

        user_id = response.data.get("id")
        user = User.objects.get(id=user_id)

        Conversation.objects.create(created_by=user)

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "user": response.data,
                "token": token.key
            },
            status=status.HTTP_201_CREATED
        )


        

@extend_schema(summary="لاگین کاربر",description="معمولا فقط مشاور برای  لاگین از این اندپوینت استفاده میکند")       
class CustomObtainAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data , context={'request':request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token , created = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data

        return Response({'token':token.key , 'user':user_data})
    
@extend_schema(summary="ساخت دانش آموز توسط مشاور")       
class CreateStudentView(CreateAPIView):
    permission_classes = [IsAuthenticated , IsMentor] 
    serializer_class   = CreatestudentSrializer


class DeleteStudentView(DestroyAPIView):
    permission_classes = [IsAuthenticated , IsMentor] 
    serializer_class   = CreatestudentSrializer
    queryset           = User.objects.filter(role="student") 

# class SendOTPView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer =  SendOtpSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         phone = serializer.validated_data.get('phone')
#         otp   =  random.randint(100000 ,999999)
#         cache.set(phone , otp , timeout=120)



#         return super().post(request, *args, **kwargs)
    

# class LoginWithOtp(APIView):    


    
@extend_schema(summary="ساخت پشتیبان توسط مشاور")       
class CreateSupportView(CreateAPIView):
    permission_classes = [IsAuthenticated , IsMentor] 
    serializer_class   = CreateSupportSerializer
    


class DeleteSupportView(DestroyAPIView):
    permission_classes = [IsAuthenticated , IsMentor] 
    serializer_class   = CreateSupportSerializer
    queryset           = User.objects.filter(role="support") 



class MentorProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsMentor]
    serializer_class   = MentorProfileSerializer

    @extend_schema(summary="دریافت پروفایل مشاور",)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(summary="ویرایش کامل پروفایل مشاور",)
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(summary="ویرایش بخشی از پروفایل مشاور",)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        return MentorProfile.objects.get(user=self.request.user)
    
class StudentProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class   = StudentProfileSerializer

    @extend_schema(summary="دریافت پروفایل دانش‌آموز",)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(summary="ویرایش کامل پروفایل دانش‌آموز",)
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(summary="ویرایش بخشی از پروفایل دانش‌آموز",)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        return StudentProfile.objects.get(user=self.request.user)

    # def get_queryset(self):
    #     pk =  self.kwargs.get('pk')
    #     return StudentProfile.objects.filter(id=pk)

class RetriveProfileStudentView(RetrieveAPIView):
    serializer_class = StudentProfileSerializer

    def get_queryset(self):
        id = self.kwargs.get('pk')
        return StudentProfile.objects.filter(id=id)
    
class RetriveProfileSupportView(RetrieveAPIView):
    serializer_class = SupportProfileSerializer

    def get_queryset(self):
        id = self.kwargs.get('pk')
        return SupportProfile.objects.filter(id=id)





class RetriveProfileStudentWithUserIdView(RetrieveAPIView):
    serializer_class = StudentProfileSerializer
    queryset = StudentProfile.objects.all()
    lookup_field = 'user_id'
    lookup_url_kwarg = 'pk'

    


    
    
class SupportProfileView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsSupport]
    serializer_class   = SupportProfileSerializer  

    @extend_schema(
        summary="دریافت پروفایل پشتیبان",)
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="ویرایش کامل پروفایل پشتیبان",)
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="ویرایش بخشی از پروفایل پشتیبان",)
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        return SupportProfile.objects.get(user=self.request.user)

@extend_schema(
    summary="دریافت Access Token جدید با استفاده از Refresh Token",
    description=(
        "زمانی که Access Token منقضی می‌شود، از این endpoint برای دریافت "
        "توکن جدید استفاده می‌شود. کافیست Refresh Token معتبر در بدنه "
        "درخواست ارسال شود. اگر Refresh Token منقضی یا نامعتبر باشد، "
        "پاسخ 401 برگردانده می‌شود و کاربر باید دوباره لاگین کند."
    ),
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "refresh": {"type": "string", "description": "Refresh Token"}
            },
            "required": ["refresh"]
        }
    },
    responses={
        200: {
            "description": "Access Token جدید صادر شد",
            "type": "object",
            "properties": {
                "access": {"type": "string"},
                "refresh": {"type": "string"}
            }
        },
        401: {
            "description": "Refresh Token نامعتبر یا منقضی است"
        }
    },
    examples=[
        OpenApiExample(
            "نمونه درخواست موفق",
            value={"refresh": "eyJhbGciOiJIUzI1NiIs..."},
            request_only=True
        ),
        OpenApiExample(
            "نمونه پاسخ موفق",
            value={
                "access": "NEW_ACCESS_TOKEN...",
                "refresh": "eyJhbGciOiJIUzI1NiIs..."
            },
            response_only=True
        ),
    ]
)
class CustomTokenRefreshView(TokenRefreshView):
    pass

class UserInfo(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.role == "mentor":
            profile = MentorProfile.objects.filter(user=user).first()
            totalStudent = self.CalculateTotalStudent()
            totalsupport = self.CalculateTotalSupport()
            serializer = MentorProfileSerializer(profile , context={'totalStudent':totalStudent ,'totalSuppurt':totalsupport , 'role':user.role})

        elif user.role == "support":
            profile = SupportProfile.objects.filter(user=user).first()
            totalStudent = self.CalculateTotalStudentForSupport(user)
            serializer = SupportProfileSerializer(profile , context={'totalStudent':totalStudent, 'role':user.role})

        else:
            profile    = StudentProfile.objects.filter(user=user).first()
            serializer = StudentProfileSerializer(profile ,context={'role':user.role})

        return Response(serializer.data)    




    def CalculateTotalStudent(self):
        return  StudentProfile.objects.all().count()
    
    def CalculateTotalSupport(self):
        return SupportProfile.objects.all().count()
    
    def CalculateTotalStudentForSupport(self , user):
        return StudentSupport.objects.filter(support=user).count()



    


    


# Create your views here.
