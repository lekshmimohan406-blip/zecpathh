from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .models import (Job,
                     Employer,
                     Candidate,
                     Application,
                     ApplicationStatusLog,
                     SavedJob,
                     AuditLog,
                     ATSScore,
                     )
from .serializers import (JobSerializer,
                        SignupSerializer,
                        EmployerSerializer,
                        CandidateSerializer,
                        ResumeUploadSerializer,
                        ApplicationSerializer,
                        EmployerApplicantSerializer,
                        SavedJobSerializer,
                        CandidateApplicationSerializer,
                        ApplicationStatusLogSerializer,
                        AuditLogSerializer,)
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated,AllowAny
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .pagination import JobPagination
from rest_framework.generics import (ListAPIView,CreateAPIView,RetrieveAPIView,UpdateAPIView,)
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter, OrderingFilter
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .resume_parser import extract_text
from .nlp_parser import parse_resume
from .ats import calculate_ats_score
from .permissions import (
    IsEmployer,
    IsCandidate,
    IsAdmin
)
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class JobListAPI(ListAPIView):
    pagination_class = JobPagination
    serializer_class = JobSerializer
    permission_classes = [AllowAny]

    filter_backends = [SearchFilter, OrderingFilter]

    search_fields = [
        "title",
        "description",
        "skills",
        "location",
    ]

    ordering_fields = [
        "created_at",
        "salary_min",
        "salary_max",
        "experience",
    ]

    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = Job.objects.select_related("employer").filter(
            is_active=True,
            status="active"
        )

        # Filter by skills
        skills = self.request.query_params.get("skills")
        if skills:
            queryset = queryset.filter(skills__icontains=skills)

        # Filter by location
        location = self.request.query_params.get("location")
        if location:
            queryset = queryset.filter(location__icontains=location)

        # Filter by job type
        job_type = self.request.query_params.get("job_type")
        if job_type:
            queryset = queryset.filter(job_type__iexact=job_type)

        # Filter by minimum experience
        min_experience = self.request.query_params.get("min_experience")
        if min_experience:
            queryset = queryset.filter(experience__gte=min_experience)

        # Filter by maximum experience
        max_experience = self.request.query_params.get("max_experience")
        if max_experience:
            queryset = queryset.filter(experience__lte=max_experience)

        # Filter by minimum salary
        min_salary = self.request.query_params.get("min_salary")
        if min_salary:
            queryset = queryset.filter(salary_min__gte=min_salary)

        # Filter by maximum salary
        max_salary = self.request.query_params.get("max_salary")
        if max_salary:
            queryset = queryset.filter(salary_max__lte=max_salary)

        # Featured jobs: newest active jobs
        featured = self.request.query_params.get("featured")
        if featured and featured.lower() == "true":
            queryset = queryset.filter(is_featured=True)

        return queryset


class EmployerJobCreateAPI(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    def post(self, request):

        employer = Employer.objects.get(user=request.user)

        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(employer=employer)

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
class EmployerJobDetailAPI(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    def get_object(self, request, job_id):

        try:
            job = Job.objects.get(
                id=job_id,
                employer__user=request.user
            )
            return job

        except Job.DoesNotExist:
            raise PermissionDenied(
                "You do not own this job or the job does not exist."
            )

    def get(self, request, job_id):

        job = self.get_object(request, job_id)
        serializer = JobSerializer(job)

        return Response(serializer.data)

    def put(self, request, job_id):

        job = self.get_object(request, job_id)

        serializer = JobSerializer(
            job,
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

        return Response(
    {
        "message": "Login successful",
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
        },
    },
    status=status.HTTP_200_OK,
)


class ProtectedAPI(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "user_id": request.user.id,
            "email": request.user.email,
            "is_authenticated": request.user.is_authenticated,
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
    
class EmployerJobStatusAPI(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    def patch(self, request, job_id):

        try:
            job = Job.objects.get(
                id=job_id,
                employer__user=request.user
            )

        except Job.DoesNotExist:
            raise PermissionDenied(
                "You do not own this job or the job does not exist."
            )

        is_active = request.data.get("is_active")

        if is_active is None:
            return Response(
                {
                    "error": "Please provide is_active: true or false"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        job.is_active = is_active
        job.status = "active" if is_active else "inactive"
        job.save()

        return Response({
            "message": "Job status updated successfully",
            "is_active": job.is_active,
            "status": job.status
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
    
class ResumeUploadAPI(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def put(self, request):

        candidate = Candidate.objects.get(
            user=request.user
        )

        serializer = ResumeUploadSerializer(
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
    
class ApplyJobAPI(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def post(self, request, job_id):

        try:
            candidate = Candidate.objects.get(
                user=request.user,
                is_deleted=False
            )
        except Candidate.DoesNotExist:
            return Response(
                {
                    "error": "Candidate profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            job = Job.objects.get(
                id=job_id,
                is_active=True,
                status="active"
            )
        except Job.DoesNotExist:
            return Response(
                {
                    "error": "This job is not available for applications."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        if Application.objects.filter(
            candidate=candidate,
            job=job
        ).exists():
            return Response(
                {
                    "error": "You have already applied for this job."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not candidate.resume:
            return Response(
                {
                    "error": "Please upload your resume before applying."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        application = Application.objects.create(
    candidate=candidate,
    job=job,
    resume_snapshot=candidate.resume_snapshot,
    status="applied"
)

        print("APPLICATION =", application)

        serializer = ApplicationSerializer(application)

        return Response(
            {
                "message": "Job application submitted successfully.",
                "application": serializer.data
            },
            status=status.HTTP_201_CREATED
        )


class CandidateApplicationListAPI(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def get(self, request):

        try:
            candidate = Candidate.objects.get(
                user=request.user,
                is_deleted=False
            )

        except Candidate.DoesNotExist:

            return Response(
                {
                    "error": "Candidate profile not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        applications = Application.objects.filter(
            candidate=candidate
        ).select_related(
            "job",
            "job__employer",
            "candidate__user"
        ).order_by(
            "-applied_at"
        )

        serializer = ApplicationSerializer(
            applications,
            many=True
        )

        return Response(
            {
                "success": True,
                "count": applications.count(),
                "applications": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
class MyApplicationsAPI(ListAPIView):

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    serializer_class = ApplicationSerializer

    def get_queryset(self):
        candidate = Candidate.objects.get(
            user=self.request.user
        )

        return Application.objects.filter(
            candidate=candidate
        ).select_related(
            "job",
            "job__employer"
        ).order_by("-applied_at")
    
class EmployerApplicationStatusAPI(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    ALLOWED_TRANSITIONS = {
        "applied": [
            "shortlisted",
            "rejected",
        ],
        "shortlisted": [
            "interview_scheduled",
            "rejected",
        ],
        "interview_scheduled": [
            "selected",
            "rejected",
        ],
        "selected": [],
        "rejected": [],
    }

    def patch(self, request, application_id):

        try:
            application = Application.objects.select_related(
                "job",
                "job__employer"
            ).get(
                id=application_id,
                job__employer__user=request.user
            )

        except Application.DoesNotExist:
            raise PermissionDenied(
                "You do not own this application or it does not exist."
            )

        new_status = request.data.get("status")

        valid_statuses = [
            "applied",
            "shortlisted",
            "interview_scheduled",
            "rejected",
            "selected",
        ]

        if new_status not in valid_statuses:
            return Response(
                {
                    "error": "Invalid status."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = application.status

        if new_status == old_status:
            return Response(
                {
                    "error": "Application already has this status."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status not in self.ALLOWED_TRANSITIONS[old_status]:
            return Response(
                {
                    "error": (
                        f"Cannot change status from "
                        f"'{old_status}' to '{new_status}'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        application.status = new_status
        application.save()

        ApplicationStatusLog.objects.create(
            application=application,
            old_status=old_status,
            new_status=new_status,
            changed_by=request.user
        )

        return Response(
            {
                "message": "Application status updated successfully.",
                "application_id": application.id,
                "old_status": old_status,
                "new_status": application.status,
                "status_updated_at": application.status_updated_at,
            }
        )
    
class EmployerMyJobsAPI(ListAPIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    serializer_class = JobSerializer

    def get_queryset(self):

        return Job.objects.filter(
            employer__user=self.request.user
        ).order_by("-created_at")
    
class EmployerJobApplicantsAPI(ListAPIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    serializer_class = EmployerApplicantSerializer

    def get_queryset(self):

        job_id = self.kwargs["job_id"]

        try:
            job = Job.objects.get(
                id=job_id,
                employer__user=self.request.user
            )
        except Job.DoesNotExist:
            raise PermissionDenied(
                "You do not own this job or it does not exist."
            )

        queryset = Application.objects.filter(
            job=job
        ).select_related(
            "candidate",
            "candidate__user"
        ).order_by("-applied_at")

        # Filter by ATS status
        status_value = self.request.query_params.get("status")
        if status_value:
            queryset = queryset.filter(status=status_value)

        # Search candidate email or skills
        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(candidate__user__email__icontains=search) |
                Q(candidate__skills__icontains=search)
            )

        return queryset
    
class EmployerJobAnalyticsAPI(APIView):

    permission_classes = [
        IsAuthenticated,
        IsEmployer
    ]

    def get(self, request, job_id):

        try:
            job = Job.objects.get(
                id=job_id,
                employer__user=request.user
            )
        except Job.DoesNotExist:
            raise PermissionDenied(
                "You do not own this job or it does not exist."
            )

        applications = Application.objects.filter(job=job)

        total_applications = applications.count()
        applied_count = applications.filter(status="applied").count()
        shortlisted_count = applications.filter(
            status="shortlisted"
        ).count()
        interview_count = applications.filter(
            status="interview_scheduled"
        ).count()
        rejected_count = applications.filter(status="rejected").count()
        selected_count = applications.filter(status="selected").count()

        shortlist_ratio = 0

        if total_applications > 0:
            shortlist_ratio = round(
                (shortlisted_count / total_applications) * 100,
                2
            )

        return Response({
            "job_id": job.id,
            "job_title": job.title,
            "total_applications": total_applications,
            "status_counts": {
                "applied": applied_count,
                "shortlisted": shortlisted_count,
                "interview_scheduled": interview_count,
                "rejected": rejected_count,
                "selected": selected_count,
            },
            "shortlist_ratio": f"{shortlist_ratio}%"
        })
    

class SaveJobAPI(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def post(self, request, job_id):

        candidate = Candidate.objects.get(user=request.user)

        job = get_object_or_404(Job, id=job_id)

        saved_job, created = SavedJob.objects.get_or_create(
            candidate=candidate,
            job=job
        )

        if not created:
            return Response(
                {"error": "Job already saved."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SavedJobSerializer(saved_job)

        return Response(serializer.data)
    
class SavedJobsListAPI(ListAPIView):

    serializer_class = SavedJobSerializer

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def get_queryset(self):

        candidate = Candidate.objects.get(
            user=self.request.user
        )

        return SavedJob.objects.filter(
            candidate=candidate
        ).select_related(
            "job",
            "job__employer"
        )
    
class UnsaveJobAPI(APIView):

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def delete(self, request, job_id):

        candidate = Candidate.objects.get(
            user=request.user
        )

        saved_job = get_object_or_404(
            SavedJob,
            candidate=candidate,
            job_id=job_id
        )

        saved_job.delete()

        return Response({
            "message": "Job removed from saved jobs."
        })
    

class CandidateInterviewStatusAPI(ListAPIView):

    serializer_class = CandidateApplicationSerializer

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def get_queryset(self):

        candidate = Candidate.objects.get(
            user=self.request.user
        )

        return Application.objects.filter(
            candidate=candidate
        ).select_related(
            "job",
            "job__employer"
        )
    
class RecommendedJobsAPI(ListAPIView):

    serializer_class = JobSerializer

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def get_queryset(self):

        candidate = Candidate.objects.get(user=self.request.user)

        if not candidate.skills:
            return Job.objects.none()

        queryset = Job.objects.filter(
            is_active=True,
            status="active"
        )

        skills = [
            skill.strip()
            for skill in candidate.skills.split()
            if skill.strip()
        ]

        query = Q()

        for skill in skills:
            query |= Q(skills__icontains=skill)

        return queryset.filter(query).distinct()
    
class ApplicationTimelineAPI(ListAPIView):

    serializer_class = ApplicationStatusLogSerializer

    permission_classes = [
        IsAuthenticated,
        IsCandidate
    ]

    def get_queryset(self):

        application = get_object_or_404(
            Application,
            id=self.kwargs["application_id"],
            candidate__user=self.request.user
        )

        return application.status_logs.all().order_by(
            "changed_at"
        )
    
class CandidateNotificationsAPI(ListAPIView):

    serializer_class = CandidateApplicationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def get_queryset(self):
        candidate = Candidate.objects.get(user=self.request.user)

        return Application.objects.filter(
            candidate=candidate
        ).exclude(
            status="applied"
        ).order_by("-status_updated_at")
    
class CandidateNotificationsAPI(ListAPIView):

    serializer_class = CandidateApplicationSerializer
    permission_classes = [IsAuthenticated, IsCandidate]

    def get_queryset(self):

        candidate = Candidate.objects.get(
            user=self.request.user
        )

        return Application.objects.filter(
            candidate=candidate
        ).exclude(
            status="applied"
        ).order_by("-status_updated_at")
    
class AdminEmployerApproveAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, employer_id):
        try:
            employer = Employer.objects.get(id=employer_id)
        except Employer.DoesNotExist:
            return Response(
                {"error": "Employer not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        employer.is_verified = True
        employer.save()

        return Response(
            {"message": "Employer approved successfully."},
            status=status.HTTP_200_OK
        )
    
class AdminBlockUserAPI(UpdateAPIView):

    permission_classes = [IsAuthenticated, IsAdmin]

    def put(self, request, user_id):

        try:
            user = User.objects.get(id=user_id)

        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        user.is_blocked = not user.is_blocked
        user.save()

        return Response(
            {
                "message": (
                    "User blocked successfully."
                    if user.is_blocked
                    else "User unblocked successfully."
                )
            },
            status=status.HTTP_200_OK
        )



class AdminSystemStatsAPI(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):

        data = {
            "total_users": User.objects.count(),
            "total_employers": Employer.objects.count(),
            "total_candidates": Candidate.objects.count(),
            "total_jobs": Job.objects.count(),
            "total_applications": Application.objects.count(),
        }

        return Response(data)
    

class AdminJobListAPI(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.all().order_by("-created_at")
    


class AdminDeactivateJobAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response(
                {"message": "Job not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        job.is_active = False
        job.save()

        return Response(
            {"message": "Job deactivated successfully."},
            status=status.HTTP_200_OK
        )
    


class AdminUserGrowthAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        data = {
            "today": User.objects.filter(date_joined__date=today).count(),
            "this_week": User.objects.filter(date_joined__date__gte=week_ago).count(),
            "this_month": User.objects.filter(date_joined__date__gte=month_ago).count(),
        }

        return Response(data)
    

class AdminAuditLogAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        logs = AuditLog.objects.all().order_by("-created_at")
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)
    

class AdminManageJobsAPI(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = JobSerializer

    def get_queryset(self):
        return Job.objects.all().order_by("-created_at")
    


class AdminJobStatusAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, job_id):

        job = get_object_or_404(Job, id=job_id)

        is_active = request.data.get("is_active")

        if is_active is None:
            return Response(
                {"error": "is_active field required"},
                status=400
            )

        job.is_active = is_active
        job.save()

        return Response({
            "message": "Job status updated successfully."
        })
    

class AdminJobActivityAPI(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):

        data = {
            "active_jobs": Job.objects.filter(is_active=True).count(),
            "inactive_jobs": Job.objects.filter(is_active=False).count(),
        }

        return Response(data)
    

class AdminDeleteJobAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, job_id):
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        job.delete()

        return Response(
            {"message": "Job deleted successfully"},
            status=status.HTTP_200_OK
        )
    
class AdminFlagUserAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        user.is_flagged = True
        user.save()

        return Response(
            {"message": "User flagged successfully."},
            status=status.HTTP_200_OK
        )
    
class AdminAuditLogAPI(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        logs = AuditLog.objects.all().order_by("-created_at")
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)
    

class ResumeParseAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.content_type)
        print(request.FILES)

        resume = request.FILES.get("resume")

        if not resume:
            return Response(
                {"error": "Resume file is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        text = extract_text(resume)

        parsed_data = parse_resume(text)

        return Response({
            "success": True,
            "text": text,
            "parsed_data": parsed_data
        })
    
class ATSMatchAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):

        print(request.content_type)
        print(request.FILES)

        resume = request.FILES.get("resume")

        if not resume:
            return Response(
                {"error": "Resume file is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            job = Job.objects.get(id=job_id)

        except Job.DoesNotExist:
            return Response(
                {"error": "Job not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Extract and parse resume
        text = extract_text(resume)
        candidate_data = parse_resume(text)

        # Calculate ATS score
        score = calculate_ats_score(candidate_data, job)

        # Determine application status
        from .automation import get_application_status
        application_status = get_application_status(score)

        # Get candidate profile
        candidate = Candidate.objects.filter(
            user=request.user
        ).first()

        if not candidate:
            return Response(
                {"error": "Candidate profile not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Save ATS Score
        ATSScore.objects.create(
            candidate=candidate,
            job=job,
            score=score
        )

        # Find existing application
        application = Application.objects.filter(
            candidate=candidate,
            job=job
        ).first()

        if application:

            old_status = application.status

            # Update application status
            if application_status == "SHORTLISTED":
                application.status = "shortlisted"

            elif application_status == "REJECTED":
                application.status = "rejected"

            else:
                application.status = "applied"

            application.save()

            # Create notification log
            from .notifications import send_application_notification

            if application.status == "shortlisted":

                send_application_notification(
                    request.user.email,
                    "Application Shortlisted",
                    f"You have been shortlisted for {job.title}"
                )

            elif application.status == "rejected":

                send_application_notification(
                    request.user.email,
                    "Application Rejected",
                    f"Your application for {job.title} was not shortlisted."
                )

            # Save status history
            ApplicationStatusLog.objects.create(
                application=application,
                old_status=old_status,
                new_status=application.status,
                changed_by=request.user
            )

        return Response({
            "success": True,
            "job": job.title,
            "ats_score": score,
            "status": application_status,
            "candidate": candidate_data
        })
class RankedCandidatesAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        scores = ATSScore.objects.order_by("-score")

        data = []

        for item in scores:
            data.append({
                "candidate_id": item.candidate.id,
                "job": item.job.title,
                "score": item.score
            })

        return Response(data)