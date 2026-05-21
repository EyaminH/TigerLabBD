from django.contrib import admin
from .models import Category, Challenge, Submission, Report

@admin.action(description='Mark selected challenges as approved')
def approve_challenges(modeladmin, request, queryset):
    queryset.update(is_approved=True)

class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'points', 'status', 'is_approved', 'created_at')
    list_filter = ('status', 'is_approved', 'category')
    search_fields = ('title', 'author__username')
    actions = [approve_challenges]

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'is_correct', 'submitted_at')
    list_filter = ('is_correct',)
    search_fields = ('user__username', 'challenge__title')

class ReportAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'reason', 'is_resolved', 'created_at')
    list_filter = ('reason', 'is_resolved')
    search_fields = ('user__username', 'challenge__title')
    actions = ['mark_resolved']

    @admin.action(description='Mark selected reports as resolved')
    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)

admin.site.register(Category)
admin.site.register(Challenge, ChallengeAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Report, ReportAdmin)
