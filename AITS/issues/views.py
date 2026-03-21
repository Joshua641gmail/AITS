
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User, Issue, Assignment, Department
from .serializers import (
    UserSerializer, IssueSerializer, AssignmentSerializer, DepartmentSerializer
)
from .permissions import IsRegistrar, IsLecturer, IsStudent, IsRegistrarOrReadOnly


# ─────────────────────────────────────────────
# Auth Views
# ─────────────────────────────────────────────

class RegisterView(APIView):
    """
    POST /api/auth/register/
    Open endpoint — anyone can register.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(request.data.get('password'))
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Returns JWT access + refresh tokens.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user is None:
            return Response(
                {'error': 'Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Blacklists the refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail': 'Logged out successfully.'}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({'error': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
# Department ViewSet
# ─────────────────────────────────────────────

class DepartmentViewSet(viewsets.ModelViewSet):
    """
    GET    /api/departments/         — list all departments (all authenticated users)
    POST   /api/departments/         — create department (registrar only)
    GET    /api/departments/{id}/    — retrieve department
    PUT    /api/departments/{id}/    — update department (registrar only)
    DELETE /api/departments/{id}/    — delete department (registrar only)
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsRegistrarOrReadOnly]


# ─────────────────────────────────────────────
# User ViewSet
# ─────────────────────────────────────────────

class UserViewSet(viewsets.ModelViewSet):
    """
    GET  /api/users/              — list users (registrar sees all; others see their own profile)
    GET  /api/users/{id}/         — retrieve user
    GET  /api/users/me/           — retrieve own profile (any authenticated user)
    GET  /api/users/lecturers/    — list lecturers (useful for assignment dropdowns)
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'registrar':
            return User.objects.all()
        # Students and lecturers can only see themselves
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """Return the currently authenticated user's profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='lecturers',
            permission_classes=[permissions.IsAuthenticated, IsRegistrar])
    def lecturers(self, request):
        """Return all lecturers — used by registrar when creating assignments."""
        department_id = request.query_params.get('department')
        qs = User.objects.filter(role='lecturer')
        if department_id:
            qs = qs.filter(department_id=department_id)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


# ─────────────────────────────────────────────
# Issue ViewSet
# ─────────────────────────────────────────────

class IssueViewSet(viewsets.ModelViewSet):
    """
    GET    /api/issues/                         — list issues (scoped by role)
    POST   /api/issues/                         — student submits a new issue
    GET    /api/issues/{id}/                    — retrieve issue
    PATCH  /api/issues/{id}/                    — update issue (student edits own pending issue)
    DELETE /api/issues/{id}/                    — delete issue (student, pending only)
    POST   /api/issues/{id}/assign/             — registrar assigns issue to a lecturer
    POST   /api/issues/{id}/update_status/      — lecturer updates status
    """
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'registrar':
            # Registrar sees all issues
            return Issue.objects.select_related('student', 'department').all()

        if user.role == 'lecturer':
            # Lecturers see only issues assigned to them
            return Issue.objects.filter(
                assignment__lecturer=user
            ).select_related('student', 'department')

        # Students see only their own issues
        return Issue.objects.filter(student=user).select_related('department')

    def perform_create(self, serializer):
        """Auto-assign the logged-in student as the issue owner."""
        if self.request.user.role != 'student':
            raise permissions.PermissionDenied("Only students can submit issues.")
        serializer.save(student=self.request.user)

    def perform_update(self, serializer):
        """Students can only edit their own pending issues."""
        issue = self.get_object()
        user = self.request.user
        if user.role == 'student':
            if issue.student != user:
                raise permissions.PermissionDenied("You can only edit your own issues.")
            if issue.status != 'pending':
                raise permissions.PermissionDenied("You can only edit issues that are still pending.")
        serializer.save()

    def perform_destroy(self, instance):
        """Students can only delete their own pending issues."""
        user = self.request.user
        if user.role == 'student':
            if instance.student != user:
                raise permissions.PermissionDenied("You can only delete your own issues.")
            if instance.status != 'pending':
                raise permissions.PermissionDenied("You cannot delete an issue that is already in progress.")
        instance.delete()

    @action(detail=True, methods=['post'], url_path='assign',
            permission_classes=[permissions.IsAuthenticated, IsRegistrar])
    def assign(self, request, pk=None):
        """
        POST /api/issues/{id}/assign/
        Body: { "lecturer": <id>, "remarks": "..." }
        Registrar assigns the issue to a lecturer.
        Department-match validation is handled in AssignmentSerializer.
        """
        issue = self.get_object()

        if hasattr(issue, 'assignment'):
            return Response(
                {'error': 'This issue has already been assigned.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = {
            'issue': issue.id,
            'lecturer': request.data.get('lecturer'),
            'remarks': request.data.get('remarks', ''),
        }
        serializer = AssignmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(registrar=request.user)
            # Update issue status to 'assigned'
            issue.status = 'assigned'
            issue.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], url_path='update_status',
            permission_classes=[permissions.IsAuthenticated, IsLecturer])
    def update_status(self, request, pk=None):
        """
        PATCH /api/issues/{id}/update_status/
        Body: { "status": "in_progress" | "resolved" }
        Lecturers can advance the status of issues assigned to them.
        """
        issue = self.get_object()
        user = request.user

        # Ensure this lecturer is actually assigned to this issue
        if not hasattr(issue, 'assignment') or issue.assignment.lecturer != user:
            return Response(
                {'error': 'You are not assigned to this issue.'},
                status=status.HTTP_403_FORBIDDEN
            )

        new_status = request.data.get('status')
        allowed_transitions = {
            'assigned': ['in_progress'],
            'in_progress': ['resolved'],
        }

        if new_status not in allowed_transitions.get(issue.status, []):
            return Response(
                {'error': f"Cannot transition from '{issue.status}' to '{new_status}'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        issue.status = new_status
        issue.save()
        return Response(IssueSerializer(issue).data)


# ─────────────────────────────────────────────
# Assignment ViewSet
# ─────────────────────────────────────────────

class AssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET  /api/assignments/        — list assignments (scoped by role)
    GET  /api/assignments/{id}/   — retrieve assignment detail
    Assignments are created via POST /api/issues/{id}/assign/
    """
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == 'registrar':
            return Assignment.objects.select_related('issue', 'lecturer', 'registrar').all()

        if user.role == 'lecturer':
            return Assignment.objects.filter(
                lecturer=user
            ).select_related('issue', 'registrar')

        # Students can see the assignment on their own issues
        return Assignment.objects.filter(
            issue__student=user
        ).select_related('issue', 'lecturer')
