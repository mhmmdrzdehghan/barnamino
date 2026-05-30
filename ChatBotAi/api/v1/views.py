from django.shortcuts import render
from rest_framework.generics import CreateAPIView , ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .tasks import AiSendMessageTask
from ChatBotAi.models import Conversation , Message
from .serializers import MessageSeralizer
import jdatetime
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema




desc = """
📡 **راهنمای ارتباط در لحظه (وب‌سوکت)**

برای دریافت پیام‌های هوش مصنوعی به صورت در لحظه، سیستم از **وب‌سوکت** استفاده می‌کند. لطفاً طبق مراحل زیر عمل کنید:

#### ۱. اتصال به وب‌سوکت
به محض ورود کاربر به صفحه گفتگو، اتصال خود را به آدرس زیر برقرار کنید:
- **آدرس:** `ws://{دامنه_سایت}/ws/chat/{شناسه_گفتگو}/`
- **وضعیت:** این اتصال باید تا زمان خروج کاربر از صفحه گفتگو برقرار بماند.

#### ۲. ارسال پیام کاربر
برای ارسال پیام، از همان مسیر قبلی استفاده کنید:
- **روش ارسال:** پست (POST)
- **مسیر:** `/ChatbotAi/message`
- **ساختار داده ارسالی:** `{"text": "متن پیام کاربر"}`

#### ۳. دریافت پاسخ هوش مصنوعی (رویداد دریافت داده)
به جای ارسال درخواست‌های مکرر و پشت‌سر‌هم (تکرار شونده) برای چک کردن پیام جدید، فقط منتظر دریافت داده روی وب‌سوکت باشید. به محض آماده شدن پاسخ از سمت سرور، داده‌ای با قالب زیر را دریافت خواهید کرد:
```json
{
    "message": "متن پاسخ تولید شده توسط هوش مصنوعی",
    "role": "assistant"
}

"""




@extend_schema(summary=" چت با ai ",description=desc)       
class ChatWithAi(APIView):

    def post(self, request, *args, **kwargs):
        conversation = Conversation.objects.filter(created_by=request.user).first()

        if not conversation:
            conversation = Conversation.objects.create(created_by=request.user)

        text = request.data.get('text')


        Message.objects.create(text=text , role='user' , conversation=conversation)
        student = request.user.Student_Profile
        data = {
            "name" :student.first_name + ' ' + student.last_name,
            "grade":student.grade,
            "field_of_study":student.field_of_study
        }


        AiSendMessageTask.delay(conversation.id , data , text , request.user.id)

        return Response({'status':'ok'})

class Messages(ListAPIView):
    serializer_class = MessageSeralizer

    def get_queryset(self):
        conversation_id = self.kwargs.get("conversation_id")

        return Message.objects.filter(
            conversation_id=conversation_id
        )
    


    
# class TestAi(APIView):
#     def post(self, request, *args, **kwargs):
#         client = OpenAI(
#             base_url='https://api.gapgpt.app/v1',
#             api_key=settings.OPENAI_API_KEY,
#             http_client=httpx.Client(verify=False) ,
#             timeout=60.0 
#         )

#         try:
#             response = client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": "Write a short bedtime story"}],
#             )

#             result = response.choices[0].message.content
#             return Response({"answer": result})

#         except Exception as e:
#             import traceback
#             print(traceback.format_exc())
#             return Response({"error": str(e), "type": str(type(e))}, status=500)




# Create your views here.
