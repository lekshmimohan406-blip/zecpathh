from rest_framework import serializers
from .models import Job
from django.contrib.auth import get_user_model
from .models import (Job,Employer,Candidate)

User = get_user_model()

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'


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

        allowed = [
            ".pdf",
            ".doc",
            ".docx"
        ]

        import os

        ext = os.path.splitext(
            value.name
        )[1].lower()

        if ext not in allowed:
            raise serializers.ValidationError(
                "Only PDF, DOC, DOCX allowed"
            )

        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError(
                "File size must be under 5MB"
            )

        return value