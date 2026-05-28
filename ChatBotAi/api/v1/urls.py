from .views import ChatWithAi , Messages
from django.urls import path , include

urlpatterns =  [
    path('message' , ChatWithAi.as_view()),
    path('messages/<int:conversation_id>' , Messages.as_view()),


]


