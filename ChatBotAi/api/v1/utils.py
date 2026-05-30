from django.conf import settings
from openai import OpenAI
from .Queris import DailyPlanData  
from School.api.v1.queries import PreparePlanDataForAI , PrepareDataInWeekAi
import json

def intent_detect(text):

    prompt = f"""
تو فقط وظیفه تشخیص intent و پارامترهای مورد نیاز را داری.

Intent های مجاز:

- daily_plan
- future_plan
- study_priority
- recovery_plan

- Report_analysis
- subject_analysis
- comparison

- educational_question
- problem_solving

- study_method

- general

قوانین:

1- فقط JSON برگردان.
2- هیچ متن اضافه‌ای ننویس.
3- اگر درس مشخص شده بود، فیلد subject را پر کن.

نمونه خروجی:

{{
    "intent":"subject_analysis",
    "subject":"ریاضی"
}}

اگر intent چیزی به جز subject_analysis بود :
{{
    "intent":"comparison",
}}



متن دانش‌آموز:

{text}
"""

    client = OpenAI(
        base_url="https://api.gapgpt.app/v1",
        api_key=settings.OPENAI_API_KEY
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "فقط JSON معتبر برگردان."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0,
        response_format={"type": "json_object"},
        max_tokens=100
    )

    return json.loads(
        response.choices[0].message.content
    )

def PrepareRagData(intent , User_id):
    if intent =="daily_plan":
        return DailyPlanData(User_id)

    # elif intent =="catch_up":
    #     return CathUpData(User_id)

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
