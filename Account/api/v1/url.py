from django.urls import path , include
from .views import Register , CustomObtainAuthToken , CreateStudentView , SupportProfileView , StudentProfileView , MentorProfileView ,CreateSupportView  , UserInfo , RetriveProfileStudentView , RetriveProfileSupportView , DeleteStudentView , DeleteSupportView , RetriveProfileStudentWithUserIdView

urlpatterns =  [
    path('mentor' , MentorProfileView.as_view() , name='mentor'),
    path('support' , SupportProfileView.as_view() , name='support'),
    path('student' , StudentProfileView.as_view() , name='student'),
    path('student/<int:pk>/' , RetriveProfileStudentView.as_view()),
    path('create-student' , CreateStudentView.as_view() , name='create-student'),
    path('delete-student/<int:pk>/' , DeleteStudentView.as_view() , name='delete-support'),
    path('delete-support/<int:pk>/' , DeleteSupportView.as_view() , name='delete-student'),
    path('create-support' , CreateSupportView.as_view() , name='create-support'),
    path('support/<int:pk>' , RetriveProfileSupportView.as_view()),
    path('GetStudentProfile/<int:pk>' , RetriveProfileStudentWithUserIdView.as_view()),
    path('' , Register.as_view()  , name='register'),
    path("login", CustomObtainAuthToken.as_view(), name="login"),
    path('me' ,UserInfo.as_view(), name='me')
]

