from rest_framework.permissions import BasePermission


class IsMentor(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "mentor"
    

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "student"  



class IsSupport(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "support"        