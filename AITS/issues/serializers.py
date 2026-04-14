from rest_framework import serializers
from .models import User, Issue, Assignment, Department

# 1. Department Serializer
class DepartmentSerializer(serializers.ModelSerializer):
    head_username = serializers.ReadOnlyField(source='head.username')

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'head', 'head_username']


# 2. User Serializer
class UserSerializer(serializers.ModelSerializer):
    # This shows the department object details when viewing a user
    department_info = DepartmentSerializer(source='department', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'department', 'department_info']
        extra_kwargs = {'password': {'write_only': True}}


# 3. Issue Serializer
class IssueSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.username')
    # Using a nested serializer for depth, but keep it read-only for display
    department_details = DepartmentSerializer(source='department', read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            'id', 'title', 'description', 'student', 'student_name', 
            'department', 'department_details','image','image_url', 'status', 'created_at', 'updated_at'
        ]
        # These fields are handled by the system, not the user input
        read_only_fields = ['status', 'student', 'created_at', 'updated_at']

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None

# 4. Assignment Serializer
class AssignmentSerializer(serializers.ModelSerializer):
    # We want to see the issue title and lecturer name in the API response
    issue_title = serializers.ReadOnlyField(source='issue.title')
    lecturer_name = serializers.ReadOnlyField(source='lecturer.username')
    registrar_name = serializers.ReadOnlyField(source='registrar.username')

    class Meta:
        model = Assignment
        fields = [
            'id', 'issue', 'issue_title', 'lecturer', 'lecturer_name', 
            'registrar', 'registrar_name', 'assigned_at', 'remarks'
        ]
        read_only_fields = ['registrar', 'assigned_at']

    def validate(self, data):
        """
        Business Logic: Ensure the lecturer belongs to the same 
        department as the issue.
        """
        lecturer = data['lecturer']
        issue = data['issue']

        if lecturer.department != issue.department:
            raise serializers.ValidationError(
                f"Conflict: Lecturer {lecturer.username} is in {lecturer.department}, "
                f"but this issue belongs to {issue.department}."
            )
        return data