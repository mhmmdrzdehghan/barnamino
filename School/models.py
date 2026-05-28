from django.db import models
from Account.models import User

class Lessons(models.Model):
    title =  models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
  

class Plan(models.Model):
    student     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plans')
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_plans')
    lesson      = models.ForeignKey(Lessons, on_delete=models.CASCADE , related_name='plans')
    date        = models.DateField()
    start       = models.TimeField(null=True, blank=True)
    end         = models.TimeField(null=True, blank=True)
    duration    = models.DurationField(null=True, blank=True)
    test_number = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)


class PlanReport(models.Model):
    plan        = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    student     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='planReports')
    lesson      = models.ForeignKey(Lessons, on_delete=models.CASCADE , related_name='planReports')
    date        = models.DateField()
    start       = models.TimeField(null=True, blank=True)
    end         = models.TimeField(null=True, blank=True)
    duration    = models.DurationField(null=True, blank=True)

    test_number = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)



class StudentSupport(models.Model):
    student  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_supports')
    support  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_students')

    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['student', 'support'], name='unique_student_support')
        ]



# Create your models here.




