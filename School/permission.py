from rest_framework.permissions import BasePermission
from .models import StudentSupport

class IsAssignedToStudent(BasePermission):
    message = "You do not have access to this student's plans."

    def has_permission(self, request, view):
        user = request.user

        if user.role =='mentor':
            return True 

        else:
            student_id = view.kwargs.get("student_id")

            exists = StudentSupport.objects.filter(support=user , student_id=student_id).exists()

            return exists

