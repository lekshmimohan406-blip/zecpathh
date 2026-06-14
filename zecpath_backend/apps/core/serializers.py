from rest_framework import serializers
from .models import Job
from django.contrib.auth import get_user_model
from rest_framework import serializers

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