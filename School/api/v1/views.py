from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from Account.permissions import IsStudent , IsMentor , IsSupport
from Account.models import StudentProfile , User , MentorProfile
from School.permission import IsAssignedToStudent
from .serializer import PlanSerializer , StudentSupportSerializer , PlanReportSerializer
from School.models import StudentSupport , Plan , PlanReport
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from openai import OpenAI
from django.conf import settings
from .queries import PrepareAiData , PrepareDataInWeekAi , PreparePlanDataForAI , PrepareAiMentor , PrepareReportAi
import json
import datetime
from .tasks import AiMentorTask , AiReportTask
from celery.result import AsyncResult
from ChatBotAi.models import AiMentorReport




class ManyPlanView(APIView):
    permission_classes = [IsAuthenticated, (IsMentor | IsSupport)]

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = PlanSerializer(
            data=request.data,
            many=True,
            context={"user": user}
        )
        # return Response(request.data[0].get('student'))
        serializer.is_valid(raise_exception=True)
        if user.role == "support":
            HasAccess = StudentSupport.objects.filter(support=user , student=request.data.get('student')).exists()
            if not HasAccess:
                raise PermissionDenied("You do not have access to this student")

        serializer.save()
        return Response(serializer.data)



class PlanView(ModelViewSet):
    # permission_classes = [IsAuthenticated, (IsMentor | IsSupport)]
    serializer_class = PlanSerializer
    def create(self, request, *args, **kwargs):
        user = request.user
        if user.role == "support":
            HasAccess = StudentSupport.objects.filter(support=user , student=request.data.get('student')).exists()
            if not HasAccess:
                raise PermissionDenied("You do not have access to this student")
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        id = self.kwargs.get('pk')
        return Plan.objects.filter(id=id)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context
    


class PlanReportsView(ModelViewSet):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = PlanReportSerializer

    def get_queryset(self):
        return PlanReport.objects.filter(student=self.request.user)
    
    
    def perform_create(self, serializer):

        return serializer.save(student=self.request.user)

@extend_schema(summary="ایجاد رابطه پشتیبانی برای یک دانش‌آموز",)       

class StudentSupportCreateView(APIView):

    permission_classes = [IsAuthenticated , IsMentor]

    def post(self, request, *args, **kwargs):
        serializer = StudentSupportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


    def delete(self, request, *args, **kwargs):
        serializer = StudentSupportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        support = serializer.validated_data['support']
        students = serializer.validated_data['students']

        StudentSupport.objects.filter(
            support=support,
            student__in=students
        ).delete()

        return Response({"message": "students removed"})


class AiMentorResultView(APIView):

    def get(self, request , user_id):
        result =  AiMentorReport.objects.filter(type='mentor' , user=user_id).order_by('-id').first()

        return Response({'result':result.result})

class AiReportResultView(APIView):

    def get(self, request, *args, **kwargs):
            result =  AiMentorReport.objects.filter(type = 'report' , user=request.user).order_by('-id').first()

            return Response({'result':result.result})

class AiReport(APIView):
    def post(self, request, *args, **kwargs):
        coach_plan     = PreparePlanDataForAI(request.user.id)
        student_report = PrepareDataInWeekAi(request.user.id)
        item_report    = PrepareReportAi(request.user.id)

        # اطمینان از json صحیح
        coach_plan_json     = json.dumps(coach_plan, ensure_ascii=False)
        student_report_json = json.dumps(student_report, ensure_ascii=False)
        item_report_json    = json.dumps(item_report, ensure_ascii=False)

        id = request.user.id
        student_name = StudentProfile.objects.filter(user=id).first().first_name

        task = AiReportTask.delay(
            request.user.id,
            student_name,
            coach_plan_json,
            student_report_json,
            item_report_json
        )

        return Response({'task_id':task.id})


class AiMentorView(APIView):

    def post(self, request, *args, **kwargs):
        id       = kwargs.get('pk')
        user     = User.objects.filter(id=id).select_related("Student_Profile").first()
        fullnameStudent = user.Student_Profile.first_name +  ' ' + user.Student_Profile.last_name 
        today = datetime.date.today() + datetime.timedelta(days=1)
        Authid = request.user
        mentor = MentorProfile.objects.filter(user=Authid).first()
        fullnameMentor = mentor.first_name + ' ' + mentor.last_name
        stats_json = PrepareAiMentor(id)

        task = AiMentorTask.delay(
            id,
            fullnameStudent,
            fullnameMentor,
            stats_json,
            str(today)
        )

        

        return Response({'task_id':task.id})


class AiResultView(APIView):

    def get(self, request, task_id):

        task_result = AsyncResult(task_id)

        if task_result.state == "PENDING":
            return Response({"status": "pending"})

        if task_result.state == "STARTED":
            return Response({"status": "processing"})

        if task_result.state == "SUCCESS":
            return Response({"status": "success" , 'result':task_result.result})

        if task_result.state == "FAILURE":
            return Response({"status": "failed"})







