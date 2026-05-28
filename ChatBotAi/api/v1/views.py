from django.shortcuts import render
from rest_framework.generics import CreateAPIView , ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .tasks import AiSendMessageTask
from ChatBotAi.models import Conversation , Message
from .serializers import MessageSeralizer
import jdatetime
from rest_framework.response import Response
from celery.result import AsyncResult
from .Queris import DailyPlanData , CathUpData
from School.api.v1.queries import PreparePlanDataForAI , PrepareDataInWeekAi
from django.conf import settings
from openai import OpenAI
from drf_spectacular.utils import extend_schema
import json
import httpx



def intent_detect(text):
    prompt = f"""
    تو فقط وظیفه تشخیص نوع درخواست دانش‌آموز را داری.


    فقط یکی از intent های زیر را برگردان:

    - daily_plan
    - catch_up
    - Report_analysis
    - study_method
    - general


    متن دانش‌آموز:
    "{text}"

    خروجی که میدی فقط باید جیسون باشد و هیچ تایپ دیگری قابل قبول نیست

    به عنوان مثال :
    {{"intent":"daily_plan"}}
    """
    
    OPENAI_API_KEY=settings.OPENAI_API_KEY
    base_url='https://api.gapgpt.app/v1'



    # return Response({'key':api_key , 'url':base_url})
    client  = OpenAI(base_url=base_url , api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        max_tokens=30
    )



    content = response.choices[0].message.content

    data = json.loads(content)

    return data["intent"]

def PrepareRagData(intent , User_id):
    if intent =="daily_plan":
        return DailyPlanData(User_id)

    elif intent =="catch_up":
        return CathUpData(User_id)

    elif intent =="Report_analysis":
        plan = PreparePlanDataForAI(User_id)
        report = PrepareDataInWeekAi(User_id) 
        return {
            "plan": plan,
            "report": report
        }
    

    elif intent == "study_method":
        return None

    else:
        return None


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
        # today        =  jdatetime.date.today().togregorian()
        conversation = Conversation.objects.filter(created_by=request.user).first()

        if not conversation:
            conversation = Conversation.objects.create(created_by=request.user)

        text = request.data.get('text')


        intent = intent_detect(text)

        # return Response(intent)

        rag_data = PrepareRagData(intent , request.user.id)

        # return Response(rag_data)

        

        Message.objects.create(text=text , role='user' , conversation=conversation)
        student = request.user.Student_Profile
        data = {
            "name" :student.first_name + ' ' + student.last_name,
            "grade":student.grade,
            "field_of_study":student.field_of_study
        }

        

        AiSendMessageTask.delay(conversation.id , data , rag_data , intent)

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
