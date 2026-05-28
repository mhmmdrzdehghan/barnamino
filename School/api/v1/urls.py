from django.urls import path , include
from rest_framework.routers import DefaultRouter
from .views import PlanView , StudentSupportCreateView , PlanView , PlanReportsView , AiMentorView , AiReport , ManyPlanView  , AiMentorResultView , AiReportResultView , AiResultView
from .queries import StudentQuery , StudentTestQuery , SupportQuery , PlanOfWeek , PlanReportOfWeek , StudentStudyQuery , TheBestItemStudyInWeekQuery , TheBestItemTestInWeekQuery , PlanAdherenceWeekQuery , TheBestStudent , TheBadStudent , StudyStudentWithDataInWeek , HouresOfStudyQuery , CartQuery 
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('planreport', PlanReportsView ,basename='planreports')
router.register('plan', PlanView , basename='plan')

urlpatterns = [
  path('' , include(router.urls)),
  path('StudentSupport' , StudentSupportCreateView.as_view()),  
  path('teststudentanalysis/<int:pk>' , StudentTestQuery.as_view()),
  path('studystudentanalysis/<int:pk>' , StudentStudyQuery.as_view()),
  path('TheBestItemTestInWeekanalysis/<int:pk>' , TheBestItemTestInWeekQuery.as_view()),
  path('TheBestItemStudyInWeekanalysis/<int:pk>' , TheBestItemStudyInWeekQuery.as_view()),
  path('PlanAdherenceWeekanalysis' , PlanAdherenceWeekQuery.as_view()),
  path('StudyStudentWithDateWeekanalysis/<int:pk>' , StudyStudentWithDataInWeek.as_view()),
  path('HouresOfStudyanalysis/<int:pk>' , HouresOfStudyQuery.as_view()),
  path('Cartanalysis' , CartQuery.as_view()),
  path('TheBestStudentanalysis' , TheBestStudent.as_view()),
  path('TheBadStudentanalysis' , TheBadStudent.as_view()),
  path('students' ,StudentQuery.as_view()),
  path('supports' ,SupportQuery.as_view()),  
  path('planWeekly/<int:pk>/' ,PlanOfWeek.as_view()),
  path('planReportWeekly/<int:pk>/' ,PlanReportOfWeek.as_view()),
  path('AiMentorView/<int:pk>/' ,AiMentorView.as_view()),
  path('Aireport' ,AiReport.as_view()),
  path('ManyPlan' ,ManyPlanView.as_view()),
  # path('AimentorResult/<int:user_id>' ,AiMentorResultView.as_view()),
  # path('AireportResult' ,AiReportResultView.as_view()),
  path('AiResult/<str:task_id>' ,AiResultView.as_view()),
] 
