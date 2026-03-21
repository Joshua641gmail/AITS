from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    DepartmentViewSet,
    UserViewSet,
    IssueViewSet,
    AssignmentViewSet,
)

# ─────────────────────────────────────────────
# Router — auto-generates standard CRUD URLs
# ─────────────────────────────────────────────

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'users',       UserViewSet,       basename='user')
router.register(r'issues',      IssueViewSet,      basename='issue')
router.register(r'assignments', AssignmentViewSet, basename='assignment')

# ─────────────────────────────────────────────
# URL Patterns
# ─────────────────────────────────────────────

urlpatterns = [

    # Auth endpoints
    path('auth/register/',      RegisterView.as_view(),   name='auth-register'),
    path('auth/login/',         LoginView.as_view(),      name='auth-login'),
    path('auth/logout/',        LogoutView.as_view(),     name='auth-logout'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),

    # All ViewSet routes (CRUD + custom actions)
    path('', include(router.urls)),
]


# ─────────────────────────────────────────────
# What the router generates automatically:
# ─────────────────────────────────────────────
#
# DEPARTMENTS
#   GET    /api/departments/           → list
#   POST   /api/departments/           → create      (registrar only)
#   GET    /api/departments/{id}/      → retrieve
#   PUT    /api/departments/{id}/      → update      (registrar only)
#   DELETE /api/departments/{id}/      → destroy     (registrar only)
#
# USERS
#   GET    /api/users/                 → list        (registrar: all | others: self)
#   GET    /api/users/{id}/            → retrieve
#   GET    /api/users/me/              → own profile (any authenticated user)
#   GET    /api/users/lecturers/       → all lecturers (registrar only)
#
# ISSUES
#   GET    /api/issues/                → list        (scoped by role)
#   POST   /api/issues/                → create      (student only)
#   GET    /api/issues/{id}/           → retrieve
#   PATCH  /api/issues/{id}/           → update      (student: own pending issues)
#   DELETE /api/issues/{id}/           → destroy     (student: own pending issues)
#   POST   /api/issues/{id}/assign/    → assign      (registrar only)
#   PATCH  /api/issues/{id}/update_status/ → update status (lecturer only)
#
# ASSIGNMENTS
#   GET    /api/assignments/           → list        (scoped by role)
#   GET    /api/assignments/{id}/      → retrieve
