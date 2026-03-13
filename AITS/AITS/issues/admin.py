from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Issue, Assignment

# 1. Customizing the User Admin to show Roles
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )

# 2. Making Issues searchable and filterable by Status
class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'student__username')
    ordering = ('-created_at',)

# 3. Assignment Admin to facilitate the Registrar's work
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('issue', 'lecturer', 'registrar', 'assigned_at')
    # Filter lecturers only in the dropdown for 'lecturer' field
    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['lecturer'].queryset = User.objects.filter(role='lecturer')
        context['adminform'].form.fields['registrar'].queryset = User.objects.filter(role='registrar')
        return super().render_change_form(request, context, *args, **kwargs)

# Registering models
admin.site.register(User, CustomUserAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Assignment, AssignmentAdmin)