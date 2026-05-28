from django.contrib import admin

from django.contrib import admin
from .models import Lessons, Plan, PlanReport , StudentSupport


# -----------------------------
#  Inline: نمایش گزارش‌های یک پلن داخل صفحه همان پلن
# -----------------------------
class PlanReportInline(admin.TabularInline):
    model = PlanReport
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = (
        'student',
        'lesson',
        'date',
        'start',
        'end',
        'test_number',
        'duration',
        'description',
        'created_at',
        'updated_at',
    )


# -----------------------------
# Lessons Admin
# -----------------------------
@admin.register(Lessons)
class LessonsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'updated_at')
    search_fields = ('title',)
    ordering = ('-created_at',)


# -----------------------------
# Plan Admin
# -----------------------------
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'student',
        'lesson',
        'date',
        'start',
        'end',
        'duration',
        'test_number',
        'created_by',
        'created_at',
    )

    list_filter = (
        'lesson',
        'student',
        'created_by',
        'date',
    )

    search_fields = (
        'student__Student_Profile__first_name',
        'student__Student_Profile__last_name',
        'lesson__title',
        'description',
        'duration',

    )

    readonly_fields = ('created_at', 'updated_at')

    inlines = [PlanReportInline]

    ordering = ('-date', '-created_at')


# -----------------------------
# PlanReport Admin
# -----------------------------
@admin.register(PlanReport)
class PlanReportAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'student',
        'lesson',
        'date',
        'start',
        'duration',
        'end',
        'test_number',
        'created_at',
    )

    list_filter = (
        'lesson',
        'student',
        'date',
    )

    search_fields = (
        'student__Student_Profile__first_name',
        'student__Student_Profile__last_name',
        'lesson__title',
        'description',
    )

    readonly_fields = ('created_at', 'updated_at')

    ordering = ('-date', '-created_at')




@admin.register(StudentSupport)
class StudentSupportAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'student',
        'support',
        'created_at',
    )

    list_filter = (
        'support',
        'created_at',
    )

    search_fields = (
        'student__username',
        'student__first_name',
        'student__last_name',
        'support__username',
        'support__first_name',
        'support__last_name',
    )

    autocomplete_fields = (
        'student',
        'support',
    )

    ordering = ('-created_at',)

    readonly_fields = (
        'created_at',
        'updated_at',
    )
