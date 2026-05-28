from openai import OpenAI
from django.conf import settings
from celery import shared_task
from ChatBotAi.models import AiMentorReport
import json
from Account.models import User

# joon madaret apload besho

@shared_task
def AiMentorTask(id , fullnameStudent ,fullnameMentor , stats_json , today):
    prompt = f"""
تو یک مشاور حرفه‌ای برنامه‌ریزی درسی هستی.

اطلاعات زیر مربوط به هفته گذشته است. این اطلاعات شامل:
- عملکرد دانش آموز در 10 روز اخیر که مجموع ساعت مطالعه و تست را برای هر درس نشون میده(report_stats)
-  برنامه‌ای که مشاور برای 10 روز اخیر تنظیم کرده بوده که مجموع ساعت مطالعه و تست را برای هر درس نشون میده(plan_stats) 
-جزئیات باکس های درسی که مشاور برای دانش آموز گذاشته در 10 روز اخیر که مجموع ساعت مطالعه و تست آن در plan_state قابل مشاهده هست(plan_items)
- درس هایی که باید بخونه هستش (lessons)


نام دانش‌آموز: {fullnameStudent}
نام مشاور: {fullnameMentor}

داده‌ها (در قالب JSON):
{stats_json}

وظیفه تو:

1. مقایسه کن که دانش‌آموز چقدر طبق برنامه مشاور پیش رفته.
2. نقاط قوت و ضعف او را در درس‌ها تشخیص بده (مثلاً در کدام درس کمتر از برنامه مطالعه کرده).
3. بر اساس این تحلیل، یک برنامه جدید و واقع‌بینانه برای هفته آینده طراحی کن که:

قوانین قطعی برنامه (اجباری):

- برنامه باید دقیقاً برای 7 روز متوالی طراحی شود.
- تاریخ شروع برنامه باید از {today} شروع شود تا 7 روز بعد
- هر روز حداقل 4 باکس درسی داشته باشد (کمتر از 4 قابل قبول نیست).
- در طول کل هفته، همه درس‌های موجود در آرایه lessons حداقل یک بار در برنامه استفاده شوند.
- تمرکز بیشتر روی درس‌هایی باشد که عملکرد ضعیف‌تری داشته‌اند.
- حجم کار بیش از حد سنگین نباشد.
- ساعت‌های پیشنهادی منطقی و قابل اجرا باشند.
- زمان‌ها با هم هم‌پوشانی نداشته باشند.
- هر باکس حداقل 60 دقیقه باشد.
- ترتیب ساعت‌ها در هر روز باید از صبح به شب مرتب باشد.


قوانین اعتبارسنجی خروجی:

- اگر حتی یک روز کمتر از 4 باکس داشته باشد، خروجی نامعتبر است.
- اگر حتی یک درس از lessons در طول هفته استفاده نشده باشد، خروجی نامعتبر است.
- باید lesson_id درست باشد تا مشکلی از بابت پیدا شدن درس پیش نیاید
- برنامه باید دقیقاً 7 روز را پوشش دهد.
- فقط JSON معتبر بازگردان.



خروجی باید فقط یک JSON معتبر با ساختار زیر باشد:

{{
"mentor_message": "یک پیام زیبا، محترمانه و امیدوارکننده خطاب به {fullnameMentor} درباره وضعیت {fullnameStudent} به همراه یک توصیه کوتاه و کاربردی برای تنظیم برنامه هفته آینده",

"schedule": [
    {{
    "student": {id},
    "lesson": "lesson_id",
    "date": "YYYY-MM-DD",
    "start": "HH:MM",
    "end": "HH:MM",
    "test_number": عدد
    }}
]
}}

قوانین مهم:
- فقط JSON خروجی بده.
- هیچ توضیح اضافی خارج از JSON ننویس.
- از markdown و backtick استفاده نکن.
- اگر تمام شرایط دقیق قابل رعایت نبود، نزدیک‌ترین برنامه معتبر را تولید کن.
هیچ‌وقت خروجی خالی تولید نکن.

"""    
    
    OPENAI_API_KEY=settings.OPENAI_API_KEY
    client = OpenAI(base_url='https://api.gapgpt.app/v1', api_key=OPENAI_API_KEY)


    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
        timeout=60
    )


    result = json.loads(response.output_text)

    return result



@shared_task
def AiReportTask(user_id , student_name , coach_plan_json , student_report_json , item_report_json):
    
    OPENAI_API_KEY=settings.OPENAI_API_KEY
    client = OpenAI(base_url='https://api.gapgpt.app/v1', api_key=OPENAI_API_KEY)

    prompt = f"""
تو یک مشاور تحصیلی مهربان، دلسوز و بسیار امیدوار هستی که دانش‌آموز عزیز ما با نام «{student_name}» را راهنمایی می‌کنی. 
لحن تو باید طوری باشد که دانش‌آموز پس از خواندن آن، احساس کند دیده شده، تشویق شده و برای هفته آینده انرژی مضاعفی دارد.

وظیفه تو تحلیل مقایسه‌ای عملکرد «{student_name}» نسبت به برنامه مشاور است.

### الزامات لحن و محتوا:
- با اسم دانش‌آموز شروع کن.
- حتما تاکید کن بر دروسی که مشاور براش گذاشته ولی درگزارشات آن دروس خوانده نشده 
- از کلمات امیدوارانه و مثبت استفاده کن.
- حتی در مورد عقب‌ماندگی‌ها، لحنت ملامت‌گر نباشد، بلکه مشوق و راه‌حل‌محور باشد.
- در بخش‌های summary، imbalances، weak_points و suggestions، **فقط و فقط متن ساده (String)** برگردان و از ساختار آرایه یا لیست در داخل این فیلدها استفاده نکن.

### ساختار خروجی (فقط JSON خالص):
{{
  "summary": "متن خلاصه (متن خالص)",
  "imbalances": "متن تحلیل تعادل مطالعه (متن خالص)",
  "weak_points": "متن راهنمایی برای دروسی که کمتر خوانده شده (متن خالص)",
  "suggestions": "متن پیشنهادهای عملی و دوستانه برای هفته بعد (متن خالص)"
}}

آنالیز کلی از برانامه ای که مشاور براش گذاشته :
{coach_plan_json}

آنالیز کلی از گزارشاتی که دانش آموز وارد کرده با توجه به برنامه ی مشاور:
{student_report_json}

باکس های درسی که مشاور وارد کرده که آنالیز آن رابرات فرستادم :
{item_report_json}
        """
    

    response = client.responses.create(
            model="gpt-4o-mini",
            input=prompt,
            timeout=60
        )
    
    result = json.loads(response.output_text)

    return result



    