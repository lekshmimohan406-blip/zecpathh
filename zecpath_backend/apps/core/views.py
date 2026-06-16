from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Job,Employer,Candidate
from .serializers import JobSerializer,SignupSerializer,EmployerSerializer,CandidateSerializer
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated

from .permissions import (
    IsEmployer,
    IsCandidate,
    IsAdmin
)
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class JobListAPI(APIView):

    def get(self, request):
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)


class JobCreateAPI(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    def post(self, request):
        serializer = JobSerializer(
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserTestAPI(APIView):

    def get(self, request):
        return Response({
            "username": "test_user",
            "message": "DRF API Working"
        })
class SignupAPI(APIView):

    def post(self, request):

        serializer = SignupSerializer(
            data=request.data
        )

        if serializer.is_valid():

            user = serializer.save()

            return Response(
                {
                    "message": "User registered successfully",
                    "email": user.email
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LoginAPI(APIView):

    def post(self, request):

        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(
            request,
            email=email,
            password=password
        )

        if user is None:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        })


class ProtectedAPI(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        return Response({
            "message": "Protected API Access Granted",
            "user": request.user.email
        })
class AdminDashboardAPI(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdmin
    ]

    def get(self, request):

        return Response({
            "message": "Admin Access Granted"
        })


class CandidateDashboardAPI(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def get(self, request):

        return Response({
            "message": "Candidate Access Granted"
        })
    

class EmployerProfileAPI(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    def get(self, request):
        employer = Employer.objects.get(user=request.user)
        serializer = EmployerSerializer(employer)
        return Response(serializer.data)

    def put(self, request):
        employer = Employer.objects.get(user=request.user)

        serializer = EmployerSerializer(
            employer,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request):
        employer = Employer.objects.get(user=request.user)
        employer.is_deleted = True
        employer.save()

        return Response({
            "message": "Profile deleted successfully"
        })
    

class CandidateProfileAPI(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def get(self, request):

        candidate = Candidate.objects.get(
            user=request.user
        )

        serializer = CandidateSerializer(
            candidate
        )

        return Response(serializer.data)

    def put(self, request):

        candidate = Candidate.objects.get(
            user=request.user
        )

        serializer = CandidateSerializer(
            candidate,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    def delete(self, request):
        candidate = Candidate.objects.get(user=request.user)
        candidate.is_deleted = True
        candidate.save()

        return Response({
            "message": "Profile deleted successfully"
        })