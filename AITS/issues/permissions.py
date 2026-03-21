from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStudent(BasePermission):
    """
    Allows access only to users with the 'student' role.
    """
    message = "Access restricted to students only."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'student'
        )


class IsLecturer(BasePermission):
    """
    Allows access only to users with the 'lecturer' role.
    """
    message = "Access restricted to lecturers only."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'lecturer'
        )


class IsRegistrar(BasePermission):
    """
    Allows access only to users with the 'registrar' role.
    """
    message = "Access restricted to the Academic Registrar only."

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'registrar'
        )


class IsRegistrarOrReadOnly(BasePermission):
    """
    Read-only access for any authenticated user.
    Write access (POST, PUT, PATCH, DELETE) restricted to registrars only.

    Used on: DepartmentViewSet
    """
    message = "Only the Academic Registrar can modify this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS') — read-only requests
        if request.method in SAFE_METHODS:
            return True

        # Write operations require registrar role
        return request.user.role == 'registrar'


class IsOwnerOrRegistrar(BasePermission):
    """
    Object-level permission.
    - Registrar can access any object.
    - Students can only access objects they own (i.e. their own issues).

    Used with: get_object() calls where per-object checks are needed.
    """
    message = "You do not have permission to access this resource."

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        # Registrar can do anything
        if request.user.role == 'registrar':
            return True

        # Students can only access their own issues
        if hasattr(obj, 'student'):
            return obj.student == request.user

        # Lecturers can access assignments linked to them
        if hasattr(obj, 'lecturer'):
            return obj.lecturer == request.user

        return False
