from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from .managers import UserManager


class User(AbstractUser):

    ADMIN = "ADMIN"
    EMPLOYER = "EMPLOYER"
    CANDIDATE = "CANDIDATE"

    ROLE_CHOICES = (
        (ADMIN, "Admin"),
        (EMPLOYER, "Employer"),
        (CANDIDATE, "Candidate"),
    )

    username = None

    email = models.EmailField(unique=True)

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=CANDIDATE
    )
    is_blocked = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Employer(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    company_name = models.CharField(
        max_length=100
    )

    company_domain = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    company_size = models.IntegerField(
        default=0
    )

    is_verified = models.BooleanField(
        default=False
    )

    is_deleted = models.BooleanField(
        default=False
    )

    def __str__(self):
        return self.company_name


class Candidate(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    skills = models.TextField()

    education = models.TextField(
        blank=True,
        null=True
    )

    experience = models.TextField(
        blank=True,
        null=True
    )

    expected_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    resume = models.FileField(
        upload_to="resumes/",
        blank=True,
        null=True
    )

    is_deleted = models.BooleanField(
        default=False
    )



class Job(models.Model):

    JOB_TYPE_CHOICES = (
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("internship", "Internship"),
        ("contract", "Contract"),
    )

    STATUS_CHOICES = (
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("closed", "Closed"),
    )

    employer = models.ForeignKey(
        Employer,
        on_delete=models.CASCADE,
        related_name="jobs",
        null=True,
        blank=True,
    )

    title = models.CharField(
        max_length=150,
        db_index=True
    )

    description = models.TextField()

    skills = models.CharField(
        max_length=500,
        db_index=True
    )

    experience = models.PositiveIntegerField(default=0)

    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)

    location = models.CharField(
        max_length=150,
        db_index=True
    )

    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        default="full_time",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
        db_index=True
    )

    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
class Application(models.Model):

    STATUS_CHOICES = (
    ("applied", "Applied"),
    ("shortlisted", "Shortlisted"),
    ("interview_scheduled", "Interview Scheduled"),
    ("rejected", "Rejected"),
    ("selected", "Selected"),
)

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    resume_snapshot = models.FileField(
        upload_to="application_resumes/",
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="applied"
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    status_updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("candidate", "job")

    def __str__(self):
        return f"{self.candidate.user.email} - {self.job.title}"
    

class ApplicationStatusLog(models.Model):

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="status_logs"
    )

    old_status = models.CharField(max_length=30)

    new_status = models.CharField(max_length=30)

    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.application.id}: "
            f"{self.old_status} → {self.new_status}"
        )
    
[
    {
        "id": 1,
        "job": 4,
        "job_title": "Senior Python Django Developer",
        "company_name": "ABC Technologies",
        "resume_snapshot": "/media/resumes/Lekshmi.Mohan_Resume.pdf",
        "status": "rejected",
        "applied_at": "2026-06-24T07:44:32.170385Z"
    }
]


class SavedJob(models.Model):

    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE,
        related_name="saved_jobs"
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="saved_by"
    )

    saved_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("candidate", "job")

    def __str__(self):
        return f"{self.candidate.user.email} - {self.job.title}"
    


class AuditLog(models.Model):
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="audit_logs"
    )
    action = models.CharField(max_length=255)
    target = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.email} - {self.action}"
    
class AuditLog(models.Model):
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="audit_logs"
    )
    action = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.email} - {self.action}"
    
class ATSScore(models.Model):
    candidate = models.ForeignKey(
        Candidate,
        on_delete=models.CASCADE
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE
    )

    score = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate} - {self.job.title} - {self.score}%"
    
class NotificationLog(models.Model):

    email = models.EmailField()

    subject = models.CharField(max_length=255)

    message = models.TextField()

    status = models.CharField(max_length=20, default="sent")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    