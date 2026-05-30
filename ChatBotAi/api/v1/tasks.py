from openai import OpenAI
from django.conf import settings
from ChatBotAi.models import Message, Conversation
from asgiref.sync import async_to_sync  
from channels.layers import get_channel_layer
from celery import shared_task
from .utils import intent_detect , PrepareRagData
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

    logger.info("intent_detect: %.3f sec",time.perf_counter() - start)


    start = time.perf_counter()
    rag_data = PrepareRagData(intent , userid)
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

    if intent == "daily_plan":
        if rag_data:
            rag_context = f"""
    [DAILY_PLAN]
    برنامه امروز دانش‌آموز:
    {rag_data}
    قوانین:
    - فقط بر اساس برنامه موجود پاسخ بده
    - اگر برنامه ناقص یا کم بود، به دانش‌آموز بگو اطلاعات برنامه محدود است
    - از خودت برنامه جدید نساز
    """
        else:
            rag_context = """
    [DAILY_PLAN]
    هیچ برنامه‌ای برای امروز ثبت نشده است.
    قوانین:
    - از خودت برنامه تولید نکن
    - اعلام کن که هنوز برنامه‌ای ثبت نشده
    - به دانش‌آموز پیشنهاد بده با مشاور خود هماهنگ کند
    """

    elif intent == "catch_up":
        if rag_data:
            rag_context = f"""
    [CATCH_UP]
    برنامه ی دانش آموز و گزارشات دانش آموز:
    {rag_data}
    قوانین:
    - فقط بر اساس اطلاعات موجود تحلیل کن
    - بر اساس اولویت های درسا با توجه به اینکه چه چیزی رو خونده و چه چیزی رو نخونده پیش نهاد بده بهش
    - اگر اطلاعات محدود بود، تحلیل را انجام بده ولی تأکید کن که داده کافی نیست
    - راهکارهای کوتاه و واقعی برای جبران پیشنهاد بده
    - اطلاعات یا برنامه ساختگی تولید نکن
    """
        else:
            rag_context = """
    [CATCH_UP]
    هیچ اطلاعاتی درباره عقب‌افتادگی دانش‌آموز ثبت نشده است.
    قوانین:
    - اعلام کن اطلاعات کافی برای بررسی وجود ندارد
    - از خودت وضعیت یا برنامه جبرانی نساز
    - پیشنهاد بده دانش‌آموز با مشاور خود هماهنگ کند
    """

    elif intent == "Report_analysis":
        if rag_data:
            rag_context = f"""
    [REPORT_ANALYSIS]
    گزارش عملکرد دانش‌آموز:
    {rag_data}
    قوانین:
    - تحلیل را فقط بر اساس داده‌های موجود انجام بده
    - اگر داده کم بود، تحلیل را انجام بده ولی تأکید کن که اطلاعات محدود است
    - نقاط ضعف و قوت را کوتاه و کاربردی توضیح بده
    - تحلیل ساختگی تولید نکن
    """
        else:
            rag_context = """
    [REPORT_ANALYSIS]
    هیچ گزارش عملکرد یا داده مطالعاتی برای دانش‌آموز ثبت نشده است.
    قوانین:
    - اعلام کن هنوز داده کافی برای تحلیل وجود ندارد
    - بگو هنوز مطالعه یا گزارشی ثبت نشده که قابل تحلیل باشد
    - از خودت تحلیل یا آمار ساختگی تولید نکن
    """

    elif intent == "study_method":
        rag_context = """
    [STUDY_METHOD]
    کاربر درباره روش مطالعه سؤال دارد.
    قوانین:
    - پاسخ کوتاه، کاربردی و آموزشی باشد
    - تکنیک‌های واقعی و قابل اجرا پیشنهاد بده
    """
    else:
        rag_context = """
    [GENERAL]
    قوانین:
    - پاسخ دوستانه و حرفه‌ای باشد
    - کوتاه و کاربردی پاسخ بده
    """

    system_prompt = f"""
    تو یک مشاور تحصیلی حرفه‌ای برای دانش‌آموزان کنکوری هستی.

    اطلاعات دانش‌آموز:
    - نام: {data["name"]}
    - پایه: {data["grade"]}
    - رشته: {data["field_of_study"]}

    Intent:
    {intent}

    Context:
    {rag_context}

    قوانین پاسخ:
    - پاسخ‌ها کوتاه، واضح و کاربردی باشند
    - لحن دوستانه و حرفه‌ای باشد
    - اگر context وجود داشت حتماً از آن استفاده کن
    - برنامه‌ریزی‌ها واقع‌بینانه باشند
    - از بولت‌پوینت استفاده کن
    - پاسخ خیلی طولانی نباشد

    محدوده عملکرد ربات:
    - این ربات فقط برای کمک به مسائل درسی، برنامه‌ریزی مطالعه، تحلیل گزارش مطالعه و روش‌های درس خواندن طراحی شده است.
    - اگر کاربر سوالی کاملاً نامرتبط با درس و تحصیل بپرسد (مثلاً دستور پخت غذا، مسائل عمومی، سرگرمی، تکنولوژی، اخبار و غیره)، مودبانه اعلام کن که این ربات فقط برای مسائل درسی و تحصیلی طراحی شده و نمی‌تواند به آن سوال پاسخ دهد.
    - در این حالت کاربر را تشویق کن که سوال خود را در زمینه درس، برنامه‌ریزی مطالعه یا تحلیل وضعیت درسی بپرسد.
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
