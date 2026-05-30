from django.conf import settings
from openai import OpenAI
from .Queris import DailyPlanData , CathUpData
from School.api.v1.queries import PreparePlanDataForAI , PrepareDataInWeekAi
import json

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
