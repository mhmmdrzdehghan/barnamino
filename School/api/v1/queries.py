from django.db.models import Sum , F , DurationField  ,ExpressionWrapper , Count
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from Account.permissions import IsStudent , IsMentor , IsSupport
from School.permission import IsAssignedToStudent
from django.utils import timezone
import jdatetime
from datetime import timedelta , datetime, date
from Account.models import StudentProfile , SupportProfile , User
from School.models import StudentSupport , PlanReport , Plan
from Account.api.v1.serializer import StudentProfileSerializer , SupportProfileSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view , OpenApiExample


class SupportQuery(ListAPIView):
    serializer_class = SupportProfileSerializer
    queryset = SupportProfile.objects.all()
    permission_classes = [IsAuthenticated ,IsMentor]

class StudentQuery(ListAPIView):
    serializer_class = StudentProfileSerializer
    queryset = StudentProfile.objects.all()
    permission_classes = [IsAuthenticated , IsMentor]

class PlanOfWeek(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        today = jdatetime.date.today()
        weekday = today.weekday()

        week_offset = int(request.query_params.get("week", 0))

        start_week = today - timedelta(days=weekday) + timedelta(weeks=week_offset)
        end_week = start_week + timedelta(days=6)

        id = kwargs.get('pk')
        user = User.objects.filter(role='student', id=id).first()
        if not user:
            return Response({"error": "user not found"}, status=404)

        query = Plan.objects.filter(
            student=user,
            date__range=(start_week.togregorian(), end_week.togregorian())
        ).select_related('lesson')

        week_days = ["شنبه","یک‌شنبه","دوشنبه","سه‌شنبه","چهارشنبه","پنج‌شنبه","جمعه"]

        days_list = []

        for i in range(7):
            day_date = start_week + timedelta(days=i)
            g_date = day_date.togregorian()

            day_reports = query.filter(date=g_date)

            items = []
            for r in day_reports:
                items.append({
                    'id'      : r.id,
                    "id_lesson":r.lesson.id,
                    "subject": r.lesson.title,
                    "solvedTests": r.test_number,
                    "description": r.description,
                    "startTime": r.start.strftime("%H:%M") if r.start else None,
                    "endTime": r.end.strftime("%H:%M") if r.end else None,
                })

            days_list.append({
                "name": week_days[i],
                "date": day_date.strftime("%Y/%m/%d"),
                "items": items
            })

        response_data = {
            "weekStart": start_week.strftime("%Y/%m/%d"),
            "weekEnd": end_week.strftime("%Y/%m/%d"),
            "weekOffset": week_offset,
            "field_of_study": user.Student_Profile.field_of_study,
            "days": days_list
        }

        return Response(response_data)

class PlanReportOfWeek(APIView):
    # permission_classes = [IsAuthenticated , IsStudent]
    def get(self, request, *args, **kwargs):

        today = jdatetime.date.today()
        weekday = today.weekday()
        id = kwargs.get('pk')
        user = User.objects.filter(id=id).first()


        week_offset = int(request.query_params.get("week", 0))

        start_week = today - timedelta(days=weekday) + timedelta(weeks=week_offset)
        end_week = start_week + timedelta(days=6)

    

        query = PlanReport.objects.filter(
            student=user,
            date__range=(start_week.togregorian(), end_week.togregorian())
        ).select_related('lesson')

        week_days = ["شنبه","یک‌شنبه","دوشنبه","سه‌شنبه","چهارشنبه","پنج‌شنبه","جمعه"]

        days_list = []

        for i in range(7):
            day_date = start_week + timedelta(days=i)
            g_date = day_date.togregorian()

            day_reports = query.filter(date=g_date)

            items = []
            for r in day_reports:
                items.append({
                    'id':r.id,
                    'id_lesson':r.lesson.id,
                    "subject": r.lesson.title,
                    "solvedTests": r.test_number,
                    "description": r.description,
                    "startTime": r.start.strftime("%H:%M") if r.start else None,
                    "endTime": r.end.strftime("%H:%M") if r.end else None,
                })

            days_list.append({
                "name": week_days[i],
                "date": day_date.strftime("%Y/%m/%d"),
                "items": items
            })

        response_data = {
            "weekStart": start_week.strftime("%Y/%m/%d"),
            "weekEnd": end_week.strftime("%Y/%m/%d"),
            "weekOffset": week_offset,
            "field_of_study": user.Student_Profile.field_of_study,
            "days": days_list
        }

        return Response(response_data)

def PrepareAiData(user_id):
    today      = jdatetime.date.today()
    weekday    = today.weekday()
    start_week = today - timedelta(days=weekday)
    end_week   = start_week + timedelta(days=6)  
    query = PlanReport.objects.filter(student=user_id , date__rng=[start_week.togregorian() , end_week.togregorian()])

    states = []
    for q in query:
        duration = q.end - q.start
        dic = {'user_id':user_id , 'lesson':q.lesson , 'tests_done':q.test_number ,'study_hours':duration}
        states.append(dic)

    data = {'StartWeek':start_week , 'EndWeek':end_week , 'states':states}

    return data

def format_timedelta_to_hhmmss(td: timedelta) -> str:
    if td is None:
        return "00:00:00"
    # مجموع ثانیه‌ها (با احتساب روزها)
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


# هم برنامه و هم گزارش های 10 روز گذشته را با مجموع ساعت و تست میدهند
def PrepareDataInWeekAi(user_id):
    today      = jdatetime.date.today()
    ten_day_ago= today - timedelta(days=9)

    qs = (
        PlanReport.objects
        .filter(
            student=user_id,
            date__gte=ten_day_ago.togregorian()
        )
        .values("lesson__title")
        .annotate(
            TotalStudy=Sum('duration'),
            TotalTest=Sum('test_number')
        )
    )

    result = []
    for row in qs:
        td = row["TotalStudy"]  # معمولاً timedelta است
        time_str = format_timedelta_to_hhmmss(td)
        result.append({
            "lesson_title": row["lesson__title"],
            "TotalStudy": time_str,
            "TotalTest": row["TotalTest"] or 0,
        })

    return result

def PreparePlanDataForAI(user_id):
    today      = jdatetime.date.today()
    ten_day_ago = today - timedelta(days=9)

    qs = (
        Plan.objects
        .filter(
            student=user_id,
            date__gte=ten_day_ago.togregorian()
        )
        .values("lesson__title")
        .annotate(
            TotalStudy=Sum('duration'),
            TotalTest=Sum('test_number')
        )
    )

    result = []
    for row in qs:
        td = row["TotalStudy"]  # معمولاً timedelta است
        time_str = format_timedelta_to_hhmmss(td)
        result.append({
            "lesson_title": row["lesson__title"],
            "TotalStudy": time_str,
            "TotalTest": row["TotalTest"] or 0,
        })

    return result




def PrepareAiMentor(user_id):
    report_stats = PrepareDataInWeekAi(user_id)
    plan_stats   = PreparePlanDataForAI(user_id)

    # آیتم‌های ریز برنامه این هفته (برای تحلیل الگوی زمانی)
    today      = jdatetime.date.today()
    ten_day_ago = today - timedelta(days=9)
    user       = StudentProfile.objects.filter(user=user_id).first()


    if user.field_of_study =="math":
        lessons = [
            { "lesson_id": 7, 'title': "آمار و احتمال" },
            { "lesson_id": 6, 'title': "گسسته" },
            { "lesson_id": 5, 'title': "هندسه" },
            { "lesson_id": 4, 'title': "شیمی" },
            { "lesson_id": 3, 'title': "فیزیک" },
            { "lesson_id": 2, 'title': "حسابان" }
        ]
        

    elif user.field_of_study =="experimental":
        lessons = [
            { "lesson_id": 9, "title": "زیست" },
            { "lesson_id": 8, "title": "ریاضی" },
            { "lesson_id": 3, "title": "فیزیک" },
            { "lesson_id": 4, "title": "شیمی" },
        ]
        
    else :
        lessons= [
            { "lesson_id": 18, "title": "روان شناسی" },
            { "lesson_id": 17, "title": "فلسفه و منطق" },
            { "lesson_id": 16, "title": "علوم اجتماعی" },
            { "lesson_id": 15, "title": "جغرافیا" },
            { "lesson_id": 14, "title": "تاریخ" },
            { "lesson_id": 13, "title": "عربی" },
            { "lesson_id": 12, "title": "ریاضی و آمار" },
            { "lesson_id": 11, "title": "علوم و فنون ادبی" },
            { "lesson_id": 10, "title": "اقتصاد" },
            ],



    plan_items = list(
        Plan.objects.filter(
            student=user_id,
            date__gte=ten_day_ago.togregorian()
        ).values(
            "date",
            "start",
            "end",
            "lesson__title",
            "test_number"
        )
    )

    return {
        "report_stats": report_stats,
        "plan_stats": plan_stats,
        "plan_items": plan_items,
        "lessons"    : lessons
    }

def PrepareReportAi(user_id):
    today      = jdatetime.date.today()
    ten_day_ago = today - timedelta(days=9)
    data = PlanReport.objects.filter(
        student_id=user_id,
        date__gte=ten_day_ago.togregorian()
    ).select_related("lesson").values(
        "student_id",
        "lesson__title",
        "duration",
        "test_number"
    )
    response = []
    for i in data:
        response.append({
            "student_id": i["student_id"],
            "lesson": i["lesson__title"],
            "duration": format_timedelta_to_hhmmss(i["duration"]),
            "test_number": i["test_number"]
        })

    return response
    
#analysis

def DatefilterOfQuery(mode, base_query, today, weekday):

    if mode == "last_week":
        end_last_week = today - timedelta(days=weekday + 1)
        start_last_week = end_last_week - timedelta(days=6)

        base_query = base_query.filter(
            date__range=[start_last_week.togregorian(), end_last_week.togregorian()]
        )

    elif mode == "this_month":
        start_of_month = today.replace(day=1).togregorian()
        last_day = jdatetime.j_days_in_month[today.month - 1]
        end_of_month = today.replace(day=last_day).togregorian()

        base_query = base_query.filter(date__range=[start_of_month, end_of_month])

    elif mode == "last_month":

        if today.month > 1:
            start_date = today.replace(month=today.month - 1, day=1)
        else:
            start_date = today.replace(year=today.year - 1, month=12, day=1)

        this_month_first_day = today.replace(day=1)
        end_date = this_month_first_day - jdatetime.timedelta(days=1)

        base_query = base_query.filter(
            date__range=[start_date.togregorian(), end_date.togregorian()]
        )

    else:
        # this_week (default)
        start_week = today - timedelta(days=weekday)
        end_week = start_week + timedelta(days=6)

        base_query = base_query.filter(
            date__range=[start_week.togregorian(), end_week.togregorian()]
        )

    return base_query
   


class StudentStudyQuery(APIView):

    def get(self, request, *args, **kwargs):
        user = kwargs.get('pk')
        base_query = PlanReport.objects.filter(student=user)
        today       = jdatetime.date.today()
        weekday     = today.weekday()
        # query = base_query
    

        lesson = request.query_params.get('lesson')
        if lesson:
            base_query = base_query.filter(lesson__title=lesson)

        mode = request.query_params.get("mode")
        filter_query =  DatefilterOfQuery(mode , base_query , today , weekday)

        data_query = (
            filter_query
            .values("lesson__title")
            .annotate(
                study_time=Sum(
                    ExpressionWrapper(
                        F("end") - F("start"),
                        output_field=DurationField()
                    )
                )
            )
        )

        # --- محاسبه جمع کل کل study_time
        total = filter_query.aggregate(
            TotalAllStudy=Sum(
                ExpressionWrapper(
                    F("end") - F("start"),
                    output_field=DurationField()
                )
            )
        )

        total_duration = total["TotalAllStudy"]

        # تبدیل total به فرمت HH:MM
        if total_duration:
            total_seconds = int(total_duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            total_formatted = f"{hours:02d}:{minutes:02d}"
        else:
            total_formatted = "00:00"

        # --- ساخت خروجی نهایی
        data = []
        for q in data_query:
            duration = q["study_time"]

            if duration:
                seconds = int(duration.total_seconds())
                h, r = divmod(seconds, 3600)
                m, _ = divmod(r, 60)
                formatted = f"{h:02d}:{m:02d}"
            else:
                formatted = "00:00"

            data.append({
                "lesson": q["lesson__title"],
                "study_time": formatted
            })

        return Response({
            "by_lessons": data,
            "total_study_time": total_formatted
        })

class StudentTestQuery(APIView):
    # permission_classes = [IsAuthenticated , IsStudent]
    @extend_schema(
    summary="گزارش تعداد تست‌های دانش‌آموز",
    description="""
    این اندپوینت تعداد تست‌های زده شده توسط دانش‌آموز را بر اساس درس برمی‌گرداند.

    فیلترها:
    - mode : بازه زمانی گزارش
        - this_week (پیشفرض)
        - last_week
        - this_month
        - last_month

    - lesson : فیلتر بر اساس نام درس (اختیاری)
    """
)
    def get(self, request, *args, **kwargs):
        user        = kwargs.get('pk')
        today       = jdatetime.date.today()
        weekday     = today.weekday()
        lesson      = request.query_params.get("lesson")
        mode        = request.query_params.get("mode")
        base_query  = PlanReport.objects.filter(student=user)

        query_with_date_filter = DatefilterOfQuery(mode , base_query , today , weekday)

        if lesson: 
            query_with_date_filter = base_query.filter(lesson=int(lesson))



        query  = query_with_date_filter.values("lesson__title").annotate(test_number=Sum("test_number"))

        total = query_with_date_filter.aggregate(total_test_number= Sum('test_number')) 

        response = {'by_lessons':query , 'total_test_number':total['total_test_number']}

        return Response(response)

class TheBestItemTestInWeekQuery(APIView):
    permission_classes = [IsAuthenticated , IsStudent]

    @extend_schema(summary='گزارش بهترین روز در هفته ی جاری بر اساس تست')

    def get(self, request, *args, **kwargs):
        user = kwargs.get('pk')
        today = jdatetime.date.today()
        weekday = today.weekday()
        start_week = today - timedelta(days=weekday)
        end_week = start_week + timedelta(days=6)
        base_query = PlanReport.objects.filter(
            student=user, date__range=[start_week.togregorian(), end_week.togregorian()]
        )
        top_day_qs = base_query.values('date').annotate(test_number=Sum('test_number')).order_by('-test_number')
        top_day = top_day_qs.first()

        if top_day:
            top_day['date'] = top_day['date'].isoformat()
            return Response(top_day)
        else:
            return Response([])

class TheBestItemStudyInWeekQuery(APIView):
    permission_classes = [IsAuthenticated , IsStudent]


    @extend_schema(summary='گزارش بهترین روز در هفته ی جاری بر اساس ساعت مطالعه')
    def get(self, request, *args, **kwargs):
        user = kwargs.get('pk')

        today = jdatetime.date.today()
        weekday = today.weekday()

        start_week = today - timedelta(days=weekday)
        end_week = start_week + timedelta(days=6)

        base_query = PlanReport.objects.filter(
            student=user,
            date__range=[start_week.togregorian(), end_week.togregorian()]
        )

        qs = base_query.values('date').annotate(duration=Sum('duration')).order_by('-duration')


        top_day = qs.first()

        if not top_day or top_day["duration"] is None:
            return Response({
                "message": "هیچ مطالعه‌ای در هفته جاری ثبت نشده است."
            }, status=404)

        total_seconds = top_day['duration'].total_seconds()
        hours, remainder = divmod(total_seconds, 3600)
        minutes, _ = divmod(remainder, 60)

        response = {
            "date": top_day['date'],
            "study": f"{int(hours):02d}:{int(minutes):02d}"
        }

        return Response(response)

class PlanAdherenceWeekQuery(APIView):
    @extend_schema(summary='میزان پایبندی به برنامه بر اساس تعداد آیتم های گزارش و آیتم های برنامه')
    def get(self, request, *args, **kwargs):
        students      =  StudentProfile.objects.values("user" , "first_name" , "last_name")

        data = []

        for student in students :
            userId = student['user']
            name   = f" {student['first_name']} {student['last_name']}"
            plan   = Plan.objects.filter(student=userId).count()
            report = PlanReport.objects.filter(student=userId).count()
            data.append({'name':name , 'plan':plan , 'report':report})


        return Response(data)

class TheBestStudent(APIView):

    @extend_schema(
            summary='گزارش 3 تا از بهترین دانش آموزان. این گزارش برای پنل مشاور هست',
            description='بر اساس ساعت مطالعه و تست با کلید filterby فیلتر میشود'
            )
    def get(self, request, *args, **kwargs):

        filterby = request.query_params.get('filterby')
        today = jdatetime.date.today()
        weekday = today.weekday()

        start_week = today - timedelta(days=weekday)
        end_week = start_week + timedelta(days=6)

        start_g = start_week.togregorian()
        end_g = end_week.togregorian()

        response = []

        # -------------------------
        # 1) بر اساس تست
        # -------------------------
        if filterby == 'test':
            data = (
                PlanReport.objects
                .filter(date__range=[start_g, end_g])
                .values('student', 'student__Student_Profile__first_name' , 'student__Student_Profile_last_name' , 'student__Student_Profile__avatar')
                .annotate(test_number=Sum('test_number'))
                .order_by('-test_number')[:3]
            )

            for d in data:
                fullname = d['student__Student_Profile__first_name'] + ' ' + d['student__Student_Profile__last_name']
                response.append({
                    'student': d['student'],
                    'StudentName': fullname,
                    'test_number': d['test_number'],
                    'avatar': d['student__Student_Profile__avatar'],

                })

        # -------------------------
        # 2) بر اساس ساعت مطالعه
        # -------------------------
        else:
            data = (
                PlanReport.objects
                .filter(date__range=[start_g, end_g])
                .values('student', 'student__Student_Profile__first_name' , 'student__Student_Profile__last_name' , 'student__Student_Profile__avatar')
                .annotate(total_study=Sum('duration'))
                .order_by('-total_study')[:3]
            )


            for d in data:
                total_seconds = d['total_study'].total_seconds()
                hours, remainder = divmod(total_seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                fullname = d['student__Student_Profile__first_name'] +' ' + d['student__Student_Profile__last_name']

                response.append({
                    'student': d['student'],
                    'StudentName': fullname,
                    'study': f"{int(hours):02d}:{int(minutes):02d}",
                    'avatar': d['student__Student_Profile__avatar'],

                })

        return Response(response)

class TheBadStudent(APIView):
    permission_classes = [IsAuthenticated ,(IsMentor|IsSupport)]
    @extend_schema(
        summary='گزارش 3 تا از بدترین دانش آموزان. این گزارش برای پنل مشاور هست',
        description='بر اساس ساعت مطالعه و تست با کلید filterby فیلتر میشود'
        )
    def get(self, request, *args, **kwargs):
        filterby = request.query_params.get('filterby')
        today = jdatetime.date.today()
        weekday = today.weekday()

        start_week = today - timedelta(days=weekday)
        end_week   = start_week + timedelta(days=6)



        response = []
        if filterby == 'test':
            data = (
                PlanReport.objects
                .filter(date__range=[start_week.togregorian() , end_week.togregorian()])
                .values('student', 'student__Student_Profile__first_name' , 'student__Student_Profile__last_name' ,'student__Student_Profile__avatar')
                .annotate(test_number=Sum('test_number'))
                .order_by('test_number')
            )[:3]

            for d in data:
                fullname = d['student__Student_Profile__first_name'] + ' ' +d['student__Student_Profile__last_name']
                response.append({
                    'test_number': d['test_number'],
                    'student': d['student'],
                    'StudentName':fullname,
                    'avatar': d['student__Student_Profile__avatar'],
                })


        else:
            

            data = (
                PlanReport.objects
                .filter(date__range=[start_week.togregorian() , end_week.togregorian()])
                .values('student', 'student__Student_Profile__first_name' , 'student__Student_Profile__last_name' ,'student__Student_Profile__avatar')
                .annotate(total_study=Sum('duration'))
                .order_by('total_study')
            )[:3]

            for d in data:
                total_seconds = d['total_study'].total_seconds()
                hours, remainder = divmod(total_seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                fullname = d['student__Student_Profile__first_name'] + ' ' +d['student__Student_Profile__last_name']

                response.append({
                    'study': f"{int(hours):02d}:{int(minutes):02d}",
                    'student': d['student'],
                    'StudentName': fullname,
                    'avatar': d['student__Student_Profile__avatar'],

                })

        return Response(response)        
                 
class StudyStudentWithDataInWeek(APIView):
    @extend_schema(summary='این گزارش برای نشان میدهد در هفته ی جاری هر درسو در هر روز چقدر خونده' ,description=' بر اساس درس هم فیلتر میشود با کلید leeson')
    def get(self, request, *args, **kwargs):

        user       = kwargs.get('pk')
        today      = jdatetime.date.today()
        weekday    = today.weekday()
        start_week = today - timedelta(days=weekday)
        end_week   = start_week + timedelta(days=6)

        base_query = PlanReport.objects.filter(
            student=user,
            date__range=[start_week.togregorian(), end_week.togregorian()]
        )



        lesson_filter = request.GET.get('lesson')
        if lesson_filter:
            base_query = base_query.filter(lesson=int(lesson_filter))

        all_lessons = list(
            base_query.values_list("lesson__title", flat=True).distinct()
        )    


        week = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه']

        data = []

        for i in range(7):
            current = start_week + timedelta(days=i)

            rows = (
                base_query.filter(date=current.togregorian())
                .values('lesson__title')
                .annotate(TotalStudy=Sum('duration'))
            )

            day_data = {lesson: 0 for lesson in all_lessons}

            for r in rows:
                td = r['TotalStudy'] or timedelta(seconds=0)
                seconds = td.total_seconds()  # ✅ Fix: convert timedelta to seconds
                day_data[r['lesson__title']] = round(seconds / 3600, 2)

            day_data['day'] = week[i]
            data.append(day_data)

        return Response(data)

class HouresOfStudyQuery(APIView):
    @extend_schema(summary='نشان میدهد هر درس چقدر خوانده شده است', description="""
    این اندپوینت تعداد تست‌های زده شده توسط دانش‌آموز را بر اساس درس برمی‌گرداند.

    فیلترها:
    - mode : بازه زمانی گزارش
        - this_week (پیشفرض)
        - last_week
        - this_month
        - last_month

    - lesson : فیلتر بر اساس نام درس (اختیاری)
    """)
    def get(self, request, *args, **kwargs):
        user       = kwargs.get('pk')
        today      = jdatetime.date.today()
        weekday    = today.weekday()
        base_query = PlanReport.objects.filter(student=user)
        mode       = request.query_params.get('mode')
        SubQuery   = DatefilterOfQuery(mode , base_query , today , weekday)
        
        data = SubQuery.values("date").annotate(TotalStudy=Sum('duration'))

        final_data = []
        for item in data:
            miladi_date = item['date'] 
            if isinstance(miladi_date, str):


                miladi_date = datetime.strptime(miladi_date, "%Y-%m-%d").date()
            jalali_date = jdatetime.date.fromgregorian(date=miladi_date)

            total_seconds = item['TotalStudy'] or 0
            if total_seconds:
                try:
                    # اگر TotalStudy به جای ثانیه، شیء timedelta باشه
                    seconds = total_seconds.total_seconds()
                except AttributeError:
                    seconds = float(total_seconds)
                td = timedelta(seconds=seconds)
                # فرمت hh:mm:ss
                hours, remainder = divmod(td.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
                # اگر بیشتر از یک روز بود
                if td.days:
                    time_str = f"{td.days*24 + hours:02}:{minutes:02}:{seconds:02}"
            else:
                time_str = "00:00:00"

            final_data.append({
                "date": jalali_date.strftime("%Y-%m-%d"),
                "TotalStudy": time_str
            })

        return Response(final_data)

class CartQuery(APIView):
    @extend_schema(summary='نشان میدهد در سه روز اخیر چه تعداد دانش آموز حداقل یک گزارش وارد کرده اند')
    def get(self, request, *args, **kwargs):
        today = datetime.today()
        three_days_ago = today - timedelta(days=2)
        base_query     = PlanReport.objects.filter(date__gte=three_days_ago)
        NumberOfPlan     = Plan.objects.filter(date__gte=three_days_ago).count()

        active = base_query.values("student").distinct().count()
        allStudent = StudentProfile.objects.all().count()
        deactive  = allStudent - active 

        numberOfReport    =   base_query.count()     

        return Response({"active":active , 'deactive':deactive , 'numberOfReport':numberOfReport , 'NumberOfPlan':NumberOfPlan})
# Ai Data 



# class TestStudentWIthDateInWeekQuery(APIView):
#     def get(self, request, *args, **kwargs):
#         user       = kwargs.get('pk')
#         today      = jdatetime.date.today()
#         weekday    = today.weekday()
#         start_week = today - timedelta(weekday)
#         end_week   = start_week + timedelta(6)


#         base_query = PlanReport.objects.filter(student=user ,date__range=[start_week , end_week])
#         lessons = base_query.values_list("lesson__title")

#         data = []

#         for l in lessons:
#             week = ['شنبه','یکشنبه','دوشنبه','سه شنبه','چهارشنبه','پنجشنبه','جمعه']
            
#             Subquery = base_query.filter(lesson__title=l)



#         return Response(lessons)



# class Syudytime