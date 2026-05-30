from openai import OpenAI
from django.conf import settings
from ChatBotAi.models import Message, Conversation
from asgiref.sync import async_to_sync  
from channels.layers import get_channel_layer
from celery import shared_task
from .utils import intent_detect , PrepareRagData
from .Queris import DailyPlanData , FuturePlanData , study_priorityAndrecovery_planAnalysis , SubjectsAnalysis , comparison
import time
import logging

logger = logging.getLogger(__name__)



@shared_task
def AiSendMessageTask(conversation_id, data,text , userid):
    task_start = time.perf_counter()
    conversation = Conversation.objects.get(id=conversation_id)
    group_name = f"chat_{conversation.id}"
    channel_layer = get_channel_layer()

    start = time.perf_counter()


    intent = intent_detect(text)


    response_intent = {
        'daily_plan': lambda: DailyPlanData(userid),
        'future_plan': lambda: FuturePlanData(userid),
        'study_priority': lambda: study_priorityAndrecovery_planAnalysis(userid),
        'recovery_plan': lambda: study_priorityAndrecovery_planAnalysis(userid),
        'subject_analysis': lambda: SubjectsAnalysis(
            userid,
            intent.get('subject')
        ),
        'comparison': lambda: comparison(userid),
    }



    logger.info("intent_detect: %.3f sec",time.perf_counter() - start)


    start = time.perf_counter()
    rag_data = response_intent.get(intent['intent'],lambda: None)()
    logger.info("PrepareRagData: %.3f sec",time.perf_counter() - start)


    start = time.perf_counter()

    messages = (
        Message.objects
        .filter(conversation=conversation)
        .order_by("-created_at")[:20]
        .values("text", "role")[::-1]
    )

    logger.info(
    "load_messages: %.3f sec",
    time.perf_counter() - start)

    rag_context = ""

    if intent['intent'] == "daily_plan":

        if rag_data:
            rag_context = f"""
    [DAILY_PLAN]

    اطلاعات برنامه امروز دانش‌آموز:
    {rag_data}

    وظیفه:
    - فقط بر اساس برنامه موجود پاسخ بده.
    - اگر کاربر درباره برنامه امروز سوال داشت از اطلاعات بالا استفاده کن.
    - برنامه جدید تولید نکن.
    - اگر اطلاعات ناقص بود اعلام کن.
    """
        else:
            rag_context = """
    [DAILY_PLAN]

    هیچ برنامه‌ای برای امروز ثبت نشده است.

    وظیفه:
    - اعلام کن برنامه‌ای ثبت نشده.
    - از خودت برنامه نساز.
    - دانش‌آموز را به هماهنگی با مشاور راهنمایی کن.
    """

    elif intent['intent'] == "future_plan":

        if rag_data:
            rag_context = f"""
    [FUTURE_PLAN]

    اطلاعات برنامه آینده:
    {rag_data}

    وظیفه:
    - فقط بر اساس برنامه ثبت شده پاسخ بده.
    - برنامه جدید تولید نکن.
    """
        else:
            rag_context = """
    [FUTURE_PLAN]

    هیچ برنامه‌ای برای بازه مورد نظر ثبت نشده است.

    وظیفه:
    - اعلام کن برنامه‌ای وجود ندارد.
    """

    elif intent['intent'] == "study_priority":

        if rag_data:
            rag_context = f"""
    [STUDY_PRIORITY]

    اطلاعات برنامه و وضعیت دانش‌آموز:
    {rag_data}

    وظیفه:
    - مهم‌ترین اولویت‌های مطالعه را مشخص کن.
    - توضیح بده دانش‌آموز بهتر است از کدام درس شروع کند.
    - اولویت‌ها را بر اساس اطلاعات موجود تعیین کن.
    """
        else:
            rag_context = """
    [STUDY_PRIORITY]

    هیچ اطلاعاتی از برنامه یا وضعیت مطالعاتی دانش‌آموز ثبت نشده است.

    وظیفه:
    - اعلام کن اطلاعات کافی برای تعیین اولویت مطالعه وجود ندارد.
    - از خودت اولویت یا برنامه ساختگی تولید نکن.
    - پیشنهاد بده دانش‌آموز برنامه و گزارش مطالعه خود را ثبت کند.
    - در صورت نیاز با مشاور خود هماهنگ کند.
    """

    elif intent['intent'] == "recovery_plan":

        if rag_data:
            rag_context = f"""
    [RECOVERY_PLAN]

    اطلاعات برنامه و میزان انجام شدن:
    {rag_data}

    وظیفه:
    - عقب‌ماندگی‌های دانش‌آموز را بررسی کن.
    - یک برنامه جبرانی سبک و واقع‌بینانه پیشنهاد بده.
    - از پیشنهادهای غیرواقعی خودداری کن.
    """
        else:
            rag_context = """
    [RECOVERY_PLAN]

    هیچ اطلاعاتی از برنامه یا گزارش‌های مطالعاتی دانش‌آموز ثبت نشده است.

    وظیفه:
    - اعلام کن اطلاعات کافی برای ارائه برنامه جبرانی وجود ندارد.
    - از خودت برنامه جبرانی یا تحلیل ساختگی تولید نکن.
    - پیشنهاد بده دانش‌آموز گزارش‌های مطالعه خود را ثبت کند.
    - در صورت نیاز برای تنظیم برنامه با مشاور خود هماهنگ کند.
    """

    elif intent['intent'] == "Report_analysis":

        if rag_data:
            rag_context = f"""
    [REPORT_ANALYSIS]

    گزارش عملکرد دانش‌آموز:
    {rag_data}

    وظیفه:
    - عملکرد را تحلیل کن.
    - نقاط قوت و ضعف را مشخص کن.
    - تحلیل فقط بر اساس داده‌های موجود باشد.
    - نتیجه‌گیری کوتاه و کاربردی ارائه بده.
    """
        else:
            rag_context = """
    [REPORT_ANALYSIS]

    هیچ گزارشی برای تحلیل وجود ندارد.

    وظیفه:
    - اعلام کن داده کافی برای تحلیل وجود ندارد.
    """

    elif intent['intent'] == "subject_analysis":

        if rag_data:
            rag_context = f"""
    [SUBJECT_ANALYSIS]

    اطلاعات درس مورد نظر:
    {rag_data}

    وظیفه:
    - فقط همین درس را تحلیل کن.
    - وضعیت درس را توضیح بده.
    - نقاط قوت و ضعف را مشخص کن.
    - اگر افت یا پیشرفت وجود دارد بیان کن.
    """
        else:
            rag_context = """
    [SUBJECT_ANALYSIS]

    هیچ اطلاعاتی برای این درس ثبت نشده است.

    وظیفه:
    - اعلام کن داده کافی برای تحلیل این درس وجود ندارد.
    - از خودت تحلیل یا آمار ساختگی تولید نکن.
    - به دانش‌آموز پیشنهاد بده گزارش مطالعه خود را ثبت کند.
    - در صورت نیاز به برنامه‌ریزی، با مشاور خود هماهنگ کند.
    """

    elif intent['intent'] == "comparison":

        if rag_data:
            rag_context = f"""
    [COMPARISON]

    اطلاعات مقایسه:
    {rag_data}

    وظیفه:
    - عملکرد فعلی را با بازه قبلی مقایسه کن.
    - پیشرفت‌ها و افت‌ها را مشخص کن.
    - جمع‌بندی کوتاه ارائه بده.
    """
        else:
            rag_context = """
    [COMPARISON]

    هیچ اطلاعاتی برای مقایسه یافت نشد.

    وظیفه:
    - اعلام کن داده کافی برای مقایسه وجود ندارد.
    - از خودت مقایسه یا نتیجه‌گیری ساختگی انجام نده.
    - به دانش‌آموز پیشنهاد بده گزارش‌های مطالعاتی خود را ثبت کند.
    - در صورت وجود مشکل در برنامه‌ریزی، با مشاور خود هماهنگ کند.
    """

    elif intent['intent'] == "study_method":

        rag_context = """
    [STUDY_METHOD]

    وظیفه:
    - روش مطالعه مناسب را توضیح بده.
    - پاسخ کاربردی و آموزشی باشد.
    - راهکارهای عملی پیشنهاد بده.
    """

    elif intent['intent'] == "educational_question":

        rag_context = """
    [EDUCATIONAL_QUESTION]

    وظیفه:
    - مفهوم درسی را آموزش بده.
    - توضیح ساده، دقیق و قابل فهم باشد.
    - در صورت نیاز مثال ارائه کن.
    """

    elif intent['intent'] == "problem_solving":

        rag_context = """
    [PROBLEM_SOLVING]

    وظیفه:
    - مسئله را مرحله به مرحله حل کن.
    - دلیل هر مرحله را توضیح بده.
    - فقط جواب نهایی را ارائه نکن.
    """

    else:

        rag_context = """
    [GENERAL]

    وظیفه:
    - پاسخ دوستانه و کوتاه باشد.
    - اگر سوال خارج از حوزه آموزشی و تحصیلی بود، اعلام کن که این سامانه برای کمک در زمینه تحصیل طراحی شده است.
    """
        

    system_prompt = f"""
    تو یک مشاور تحصیلی حرفه‌ای برای دانش‌آموزان کنکوری هستی.

    اطلاعات دانش‌آموز:

    نام: {data["name"]}
    پایه: {data["grade"]}
    رشته: {data["field_of_study"]}

    Intent:
    {intent['intent']}

    Context:
    {rag_context}

    قوانین عمومی:

    - فقط بر اساس Context پاسخ بده.
    - اگر اطلاعات کافی وجود نداشت صادقانه اعلام کن.
    - اطلاعات ساختگی تولید نکن.
    - پاسخ‌ها کوتاه، واضح و کاربردی باشند.
    - از بولت پوینت استفاده کن.
    - لحن دوستانه و حرفه‌ای باشد.
    - در تحلیل‌ها روی اقدام عملی تمرکز کن.
    - اگر سوال آموزشی بود نقش معلم را داشته باش.
    - اگر سوال برنامه‌ریزی بود نقش مشاور را داشته باش.
    - اگر سوال تحلیلی بود نقش تحلیل‌گر عملکرد را داشته باش.

    محدوده فعالیت:

    این سامانه فقط برای:
    - برنامه‌ریزی درسی
    - تحلیل عملکرد
    - روش مطالعه
    - آموزش دروس
    - حل تمرین و سوالات درسی

    طراحی شده است.

    اگر سوال خارج از این حوزه‌ها بود، مودبانه اعلام کن که تنها در زمینه آموزش و تحصیل می‌توانی کمک کنی.
    """


    llm_messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    for msg in messages:
        llm_messages.append({
            "role": msg["role"],
            "content": msg["text"]
        })

    ai_text = ""

    base_url = 'https://api.gapgpt.app/v1'
    client = OpenAI(
        base_url=base_url,
        api_key=settings.OPENAI_API_KEY
    )

    start = time.perf_counter()


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=llm_messages,
        stream=True,
        timeout=60
    )

    logger.info(
    "openai_connect: %.3f sec",
    time.perf_counter() - start)


    stream_start = time.perf_counter()
    first_chunk = True

    for chunk in response:

        if first_chunk:
            logger.info(
                "first_chunk: %.3f sec",
                time.perf_counter() - stream_start
            )
            first_chunk = False

        if len(chunk.choices) > 0:
            content = chunk.choices[0].delta.content

            if content:
                ai_text += content

                async_to_sync(channel_layer.group_send)(
                    group_name,
                    {
                        "type": "ai_message",
                        "text": content,
                        "role": "assistant"
                    }
                )
    logger.info(
    "stream_total: %.3f sec",
    time.perf_counter() - stream_start)           



    async_to_sync(channel_layer.group_send)(
    group_name,
    {
        "type": "stream_done",
        "full_text": ai_text
    }
)            

    Message.objects.create(
        conversation=conversation,
        role="assistant",
        text=ai_text
    )

    logger.info(
    "task_total: %.3f sec",
    time.perf_counter() - task_start)

    return ai_text
