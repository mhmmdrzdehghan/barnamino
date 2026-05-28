from School.models import Plan , PlanReport
import jdatetime


def format_timedelta_to_hhmmss(td) -> str:
    if td is None:
        return "00:00:00"
    # مجموع ثانیه‌ها (با احتساب روزها)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def DailyPlanData(user_id):

    today = jdatetime.date.today().togregorian()

    query = (
        Plan.objects
        .filter(student=user_id, date=today)
        .select_related("lesson")
        .values("lesson__title", "duration", "test_number")
    )

    data = []

    for i in query:

        totalStudy = format_timedelta_to_hhmmss(i["duration"])

        data.append({
            "lesson": i["lesson__title"],
            "test_number": i["test_number"],
            "TotalStudy": totalStudy
        })

    return data

def CathUpData(user_id):

    plan = DailyPlanData(user_id)

    today = jdatetime.date.today().togregorian()

    query = (
        PlanReport.objects
        .filter(student=user_id, date=today)
        .values("lesson_title", "duration", "test_number")
    )

    data = []

    for i in query:

        totalStudy = format_timedelta_to_hhmmss(i["duration"])

        data.append({
            "lesson": i["lesson_title"],
            "test_number": i["test_number"],
            "TotalStudy": totalStudy
        })

    report = data

    result = [plan, report]

    return result

