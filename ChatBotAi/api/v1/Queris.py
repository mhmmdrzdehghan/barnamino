from School.models import Plan , PlanReport
import jdatetime , datetime
from django.db.models import Sum 


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

# def CathUpData(user_id):

#     plan = DailyPlanData(user_id)

#     today = jdatetime.date.today().togregorian()

#     query = (
#         PlanReport.objects
#         .filter(student=user_id, date=today)
#         .values("lesson_title", "duration", "test_number")
#     )

#     data = []

#     for i in query:

#         totalStudy = format_timedelta_to_hhmmss(i["duration"])

#         data.append({
#             "lesson": i["lesson_title"],
#             "test_number": i["test_number"],
#             "TotalStudy": totalStudy
#         })

#     report = data

#     result = [plan, report]

#     return result

def FuturePlanData(user_id):
    today    = jdatetime.date.today().togregorian()
    tommorow = today + datetime.timedelta(days=1)

    query = (
        Plan.objects.
        filter(student=user_id , date=tommorow).
        select_related("lesson").
        values("lesson__title", "duration", "test_number")
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
    
def TodayProgress(user_id):
    today = jdatetime.date.today().togregorian()

    query =( 
        PlanReport.objects.
        filter(student=user_id , date=today).
        select_related('lesson').
        values('lesson__title' , 'test_number' , 'duration')
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

def SubjectsAnalysis(user_id, sub=None):

    today = jdatetime.date.today().togregorian()

    plan = (
        Plan.objects
        .filter(
            student=user_id,
            date=today,
            lesson__title=sub
        )
        .aggregate(
            planned_tests=Sum("test_number"),
            planned_duration=Sum("duration")
        )
    )

    report = (
        PlanReport.objects
        .filter(
            student=user_id,
            date=today,
            lesson__title=sub
        )
        .aggregate(
            actual_tests=Sum("test_number"),
            actual_duration=Sum("duration")
        )
    )

    planned_tests = plan["planned_tests"] or 0
    actual_tests = report["actual_tests"] or 0

    planned_duration = plan["planned_duration"]
    actual_duration = report["actual_duration"]

    planned_hours = (
        round(planned_duration.total_seconds() / 3600, 2)
        if planned_duration
        else 0
    )

    actual_hours = (
        round(actual_duration.total_seconds() / 3600, 2)
        if actual_duration
        else 0
    )

    completion_rate = 0

    if planned_hours:
        completion_rate = round(
            (actual_hours / planned_hours) * 100,
            1
        )

    return {
        "lesson": sub,
        "planned_tests": planned_tests,
        "actual_tests": actual_tests,
        "planned_hours": planned_hours,
        "actual_hours": actual_hours,
        "completion_rate": completion_rate
    }    

def comparison(user_id):

    today = jdatetime.date.today().togregorian()

    weekday = today.weekday()

    start_current_week = today - datetime.timedelta(days=weekday)

    start_previous_week = start_current_week - datetime.timedelta(days=7)
    end_previous_week = start_current_week - datetime.timedelta(days=1)

    current_week = (
        PlanReport.objects
        .filter(
            student=user_id,
            date__gte=start_current_week
        )
        .values("lesson__title")
        .annotate(
            totaltest=Sum("test_number"),
            totalstudy=Sum("duration")
        )
    )

    previous_week = (
        PlanReport.objects
        .filter(
            student=user_id,
            date__range=(start_previous_week, end_previous_week)
        )
        .values("lesson__title")
        .annotate(
            totaltest=Sum("test_number"),
            totalstudy=Sum("duration")
        )
    )

    current_dict = {
        item["lesson__title"]: item
        for item in current_week
    }

    previous_dict = {
        item["lesson__title"]: item
        for item in previous_week
    }

    lessons = set(current_dict.keys()) | set(previous_dict.keys())

    result = []

    for lesson in lessons:

        current = current_dict.get(lesson, {})
        previous = previous_dict.get(lesson, {})

        current_hours = (
            round(current["totalstudy"].total_seconds() / 3600, 2)
            if current.get("totalstudy")
            else 0
        )

        previous_hours = (
            round(previous["totalstudy"].total_seconds() / 3600, 2)
            if previous.get("totalstudy")
            else 0
        )

        current_tests = current.get("totaltest") or 0
        previous_tests = previous.get("totaltest") or 0

        result.append({
            "lesson": lesson,

            "current_hours": current_hours,
            "previous_hours": previous_hours,
            "hours_change": round(
                current_hours - previous_hours,
                2
            ),

            "current_tests": current_tests,
            "previous_tests": previous_tests,
            "tests_change": current_tests - previous_tests,
        })

    return result    

def study_priorityAndrecovery_planAnalysis(user_id):
    today_progress = TodayProgress(user_id)
    today_plan = DailyPlanData(user_id)
    tomorrow_plan = FuturePlanData(user_id)

    return {
        'today_progress':today_progress,
        'today_plan':today_plan,
        'tomorrow_plan':tomorrow_plan
    }

