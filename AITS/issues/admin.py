from django.contrib import admin

# Register your models here.

from django.contrib.auth.admin import UserAdmin
from .models import User, Issue, Assignment, Department
 
 
# ─────────────────────────────────────────────
# Department Admin
# ─────────────────────────────────────────────
 
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ['name', 'code', 'head', 'created_at']
    search_fields = ['name', 'code']
    ordering      = ['name']
 
 
# ─────────────────────────────────────────────
# User Admin
# ─────────────────────────────────────────────
 
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Columns shown in the user list page
    list_display   = ['username', 'email', 'role', 'department', 'is_active']
    list_filter    = ['role', 'department', 'is_active']
    search_fields  = ['username', 'email']
    ordering       = ['username']
 
    # Add 'role' and 'department' to the user detail page
    fieldsets = UserAdmin.fieldsets + (
        ('Academic Info', {
            'fields': ('role', 'department')
        }),
    )
 
    # Add 'role' and 'department' to the create user page
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Academic Info', {
            'fields': ('role', 'department')
        }),
    )
 
 
# ─────────────────────────────────────────────
# Issue Admin
# ─────────────────────────────────────────────
 
@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display   = ['title', 'student', 'department', 'status', 'created_at']
    list_filter    = ['status', 'department']
    search_fields  = ['title', 'student__username']
    ordering       = ['-created_at']  # newest first
    readonly_fields = ['created_at', 'updated_at']
 
 
# ─────────────────────────────────────────────
# Assignment Admin
# ─────────────────────────────────────────────
 
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display  = ['issue', 'lecturer', 'registrar', 'assigned_at']
    search_fields = ['issue__title', 'lecturer__username']
    ordering      = ['-assigned_at']  # newest first
    readonly_fields = ['assigned_at']
 
