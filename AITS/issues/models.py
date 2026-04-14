from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):

    ROLE_CHOICE = (
        ('student','Student'),
        ('registrar','Academic Registrar'),
        ('lecturer','Lecturer'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICE)
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'
    )
    pass

class Issue(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    student = models.ForeignKey(User, on_delete = models.CASCADE, related_name='submitted_isssues')
    student = models.ForeignKey(User, on_delete = models.CASCADE, related_name='submitted_issues')
    department = models.ForeignKey(
        'Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='issues'
    )
    image = models.ImageField(
        upload_to='issue_images/',
        blank=True,
        null=True,
        help_text='Optional: Upload an image related to the issue'
    )
    image = models.ImageField(upload_to='issue_images/', blank=True, null=True)
    status = models.CharField(max_length=200, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Assignment(models.Model):
    issue = models.OneToOneField(Issue, on_delete=models.CASCADE, related_name='assignment')
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    lecturer = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'lecturer'}, related_name='assigned_tasks')
    registrar = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='processed_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Issue: {self.issue.title} assigned to {self.lecturer.username}"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)  # e.g. "CS", "ENG", "MED"
    head = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments', limit_choices_to={'role': 'lecturer'} )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} - {self.name}"