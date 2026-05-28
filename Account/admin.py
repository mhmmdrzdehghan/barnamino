from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms

from .models import User, StudentProfile, MentorProfile, SupportProfile


class UserAdmin(BaseUserAdmin):
    list_display = ("id", "email", "phone", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("email", "phone")
    ordering = ("-id",)

    fieldsets = (
        ("اطلاعات ورود", {"fields": ("email", "password")}),
        ("مشخصات کاربر", {"fields": ("phone", "role")}),
        ("دسترسی‌ها", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("تاریخ‌ها", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        ("ایجاد کاربر جدید", {
            "classes": ("wide",),
            "fields": ("email", "phone", "role", "password1", "password2"),
        }),
    )


admin.site.register(User, UserAdmin)


class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    extra = 0
    can_delete = False
    verbose_name_plural = "Student Profile"


class MentorProfileInline(admin.StackedInline):
    model = MentorProfile
    extra = 0
    can_delete = False
    verbose_name_plural = "Mentor Profile"


class SupportProfileInline(admin.StackedInline):
    model = SupportProfile
    extra = 0
    can_delete = False
    verbose_name_plural = "Support Profile"


class UserAdmin(BaseUserAdmin):
    inlines = [StudentProfileInline, MentorProfileInline, SupportProfileInline]



@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "first_name",
        "last_name",
        "grade",
        "field_of_study",
        "name_of_school",
        "gender",
        # "get_supports"
    )

    search_fields = ("user__email", "first_name", "last_name")
    list_filter = ("grade", "field_of_study")


@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "first_name", "last_name")
    search_fields = ("user__email", "first_name", "last_name")


@admin.register(SupportProfile)
class SupportProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "first_name", "last_name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("user__email",)



