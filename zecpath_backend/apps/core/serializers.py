from rest_framework import serializers
from .models import Job
from django.contrib.auth import get_user_model
from .models import (Job,
                    Employer,
                    Candidate,
                    Application,
                    SavedJob,
                    ApplicationStatusLog,
                    AuditLog,)
from .models import SavedJob

User = get_user_model()

class JobSerializer(serializers.ModelSerializer):

    employer_name = serializers.CharField(
        source="employer.company_name",
        read_only=True
    )

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "description",
            "skills",
            "experience",
            "salary_min",
            "salary_max",
            "location",
            "job_type",
            "status",
            "is_active",
            "employer",
            "employer_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "employer",
            "created_at",
            "updated_at",
        ]


class SignupSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "phone",
            "role"
        ]

    def create(self, validated_data):

        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user
    

class EmployerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employer
        fields = "__all__"


class CandidateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        fields = "__all__"


class ResumeUploadSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Candidate
        fields = ["resume"]

    def validate_resume(self, value):
        if not value.name.lower().endswith(".pdf"):
            raise serializers.ValidationError(
                "Only PDF files are allowed."
            )

        max_size = 5 * 1024 * 1024

        if value.size > max_size:
            raise serializers.ValidationError(
                "Resume file size must be less than 5 MB."
            )

        return value
    

class SavedJobSerializer(serializers.ModelSerializer):

    job_title = serializers.CharField(
        source="job.title",
        read_only=True
    )

    company_name = serializers.CharField(
        source="job.employer.company_name",
        read_only=True
    )

    class Meta:
        model = SavedJob
        fields = [
            "id",
            "job",
            "job_title",
            "company_name",
            "saved_at",
        ]
    

class ApplicationSerializer(serializers.ModelSerializer):

    job_title = serializers.CharField(
        source="job.title",
        read_only=True
    )

    company_name = serializers.CharField(
        source="job.employer.company_name",
        read_only=True
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "job",
            "job_title",
            "company_name",
            "resume_snapshot",
            "status",
            "applied_at",
        ]

        read_only_fields = [
            "job",
            "job_title",
            "company_name",
            "resume_snapshot",
            "status",
            "applied_at",
        ]

class EmployerApplicantSerializer(serializers.ModelSerializer):

    candidate_email = serializers.EmailField(
        source="candidate.user.email",
        read_only=True
    )

    candidate_skills = serializers.CharField(
        source="candidate.skills",
        read_only=True
    )

    candidate_education = serializers.CharField(
        source="candidate.education",
        read_only=True
    )

    candidate_experience = serializers.CharField(
        source="candidate.experience",
        read_only=True
    )

    candidate_resume = serializers.FileField(
        source="resume_snapshot",
        read_only=True
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "candidate_email",
            "candidate_skills",
            "candidate_education",
            "candidate_experience",
            "candidate_resume",
            "status",
            "applied_at",
            "status_updated_at",
        ]

class SavedJobSerializer(serializers.ModelSerializer):

    job_title = serializers.CharField(
        source="job.title",
        read_only=True
    )

    company_name = serializers.CharField(
        source="job.employer.company_name",
        read_only=True
    )

    class Meta:
        model = SavedJob
        fields = [
            "id",
            "job",
            "job_title",
            "company_name",
            "saved_at",
        ]


class CandidateApplicationSerializer(serializers.ModelSerializer):

    job_title = serializers.CharField(
        source="job.title",
        read_only=True
    )

    company_name = serializers.CharField(
        source="job.employer.company_name",
        read_only=True
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "job",
            "job_title",
            "company_name",
            "status",
            "applied_at",
        ]

class ApplicationStatusLogSerializer(serializers.ModelSerializer):

    changed_by = serializers.CharField(
        source="changed_by.email",
        read_only=True
    )

    class Meta:
        model = ApplicationStatusLog
        fields = [
            "old_status",
            "new_status",
            "changed_by",
            "changed_at",
        ]



class AuditLogSerializer(serializers.ModelSerializer):
    admin = serializers.CharField(source="admin.email")

    class Meta:
        model = AuditLog
        fields = [
            "admin",
            "action",
            "target",
            "created_at",
        ]

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"