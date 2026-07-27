from django.urls import path

from .views import (
    JobListAPI,
    UserTestAPI,
    SignupAPI,
    LoginAPI,
    ProtectedAPI,
    AdminDashboardAPI,
    CandidateDashboardAPI,
    EmployerProfileAPI,
    CandidateProfileAPI,
    ResumeUploadAPI,
    EmployerJobCreateAPI,
    EmployerJobDetailAPI,
    EmployerJobStatusAPI,
    ApplyJobAPI,
    CandidateApplicationListAPI,
    MyApplicationsAPI,
    EmployerApplicationStatusAPI,
    EmployerMyJobsAPI,
    EmployerJobApplicantsAPI,
    EmployerJobAnalyticsAPI,
    SaveJobAPI,
    SavedJobsListAPI,
    UnsaveJobAPI,
    CandidateInterviewStatusAPI,
    RecommendedJobsAPI,
    ApplicationTimelineAPI,
    CandidateNotificationsAPI,
    AdminEmployerApproveAPI,
    AdminBlockUserAPI,
    AdminSystemStatsAPI,
    AdminJobListAPI,
    AdminDeactivateJobAPI,
    AdminUserGrowthAPI,
    AdminAuditLogAPI,
    AdminManageJobsAPI,
    AdminJobStatusAPI,
    AdminJobActivityAPI,
    AdminDeleteJobAPI,
    AdminFlagUserAPI,
    ResumeParseAPI,
    ATSMatchAPI,
    RankedCandidatesAPI,
    
)

urlpatterns = [
    # Job list
    path("jobs/", JobListAPI.as_view(), name="job-list"),

    # User and authentication
    path("user/", UserTestAPI.as_view()),
    path("signup/", SignupAPI.as_view()),
    path("login/", LoginAPI.as_view()),
    path("protected/", ProtectedAPI.as_view()),

    # Dashboards
    path("admin-dashboard/", AdminDashboardAPI.as_view()),
    path("candidate-dashboard/", CandidateDashboardAPI.as_view()),

    # Profiles and resume
    path("employer-profile/", EmployerProfileAPI.as_view()),
    path("candidate-profile/", CandidateProfileAPI.as_view()),
    path("resume-upload/", ResumeUploadAPI.as_view()),

    # Employer job management
    path(
        "employer/jobs/create/",
        EmployerJobCreateAPI.as_view(),
        name="employer-job-create",
    ),
    path(
        "employer/jobs/<int:job_id>/",
        EmployerJobDetailAPI.as_view(),
        name="employer-job-detail",
    ),
    path(
        "employer/jobs/<int:job_id>/status/",
        EmployerJobStatusAPI.as_view(),
        name="employer-job-status",
    ),

    path(
    "jobs/<int:job_id>/apply/",
    ApplyJobAPI.as_view(),
    name="apply-job"
),

path(
    "candidate/applications/",
    CandidateApplicationListAPI.as_view(),
    name="candidate-applications"
),

path(
    "my-applications/",
    MyApplicationsAPI.as_view(),
    name="my-applications"
),

path(
    "employer/applications/<int:application_id>/status/",
    EmployerApplicationStatusAPI.as_view(),
    name="employer-application-status"
),

path(
    "employer/jobs/",
    EmployerMyJobsAPI.as_view(),
    name="employer-my-jobs"
),

path(
    "employer/jobs/<int:job_id>/applicants/",
    EmployerJobApplicantsAPI.as_view(),
    name="employer-job-applicants"
),

path(
    "employer/jobs/<int:job_id>/analytics/",
    EmployerJobAnalyticsAPI.as_view(),
    name="employer-job-analytics"
),

path(
    "jobs/<int:job_id>/save/",
    SaveJobAPI.as_view(),
    name="save-job",
),

path(
    "candidate/saved-jobs/",
    SavedJobsListAPI.as_view(),
    name="saved-jobs",
),

path(
    "jobs/<int:job_id>/unsave/",
    UnsaveJobAPI.as_view(),
    name="unsave-job",
),

path(
    "candidate/interview-status/",
    CandidateInterviewStatusAPI.as_view(),
    name="candidate-interview-status",
),

path(
    "candidate/recommendations/",
    RecommendedJobsAPI.as_view(),
    name="candidate-recommendations",
),

path(
    "applications/<int:application_id>/timeline/",
    ApplicationTimelineAPI.as_view(),
    name="application-timeline",
),

path(
    "candidate/notifications/",
    CandidateNotificationsAPI.as_view(),
    name="candidate-notifications",
),

path(
    "candidate/notifications/",
    CandidateNotificationsAPI.as_view(),
    name="candidate-notifications",
),

path(
    "admin/employers/<int:employer_id>/approve/",
    AdminEmployerApproveAPI.as_view(),
    name="admin-employer-approve",
),

path(
    "admin/users/<int:user_id>/block/",
    AdminBlockUserAPI.as_view(),
    name="admin-block-user",
),

path(
    "admin/system-stats/",
    AdminSystemStatsAPI.as_view(),
    name="admin-system-stats",
),

path(
    "admin/jobs/",
    AdminJobListAPI.as_view(),
    name="admin-job-list",
),

path(
    "admin/jobs/<int:job_id>/deactivate/",
    AdminDeactivateJobAPI.as_view(),
    name="admin-deactivate-job",
),

path(
    "admin/user-growth/",
    AdminUserGrowthAPI.as_view(),
    name="admin-user-growth",
),

path(
    "admin/audit-logs/",
    AdminAuditLogAPI.as_view(),
    name="admin-audit-logs",
),

path(
    "admin/jobs/",
    AdminManageJobsAPI.as_view(),
    name="admin-manage-jobs",
),

path(
    "admin/jobs/<int:job_id>/status/",
    AdminJobStatusAPI.as_view(),
    name="admin-job-status",
),

path(
    "admin/job-activity/",
    AdminJobActivityAPI.as_view(),
    name="admin-job-activity",
),

path(
    "admin/jobs/<int:job_id>/",
    AdminDeleteJobAPI.as_view(),
    name="admin-delete-job",
),

path(
    "admin/users/<int:user_id>/flag/",
    AdminFlagUserAPI.as_view(),
),

path(
    "admin/audit-logs/",
    AdminAuditLogAPI.as_view(),
),

path(
    "resume/parse/",
    ResumeParseAPI.as_view(),
    name="resume-parse",
),

path(
    "jobs/<int:job_id>/match/",
    ATSMatchAPI.as_view(),
    name="ats-match",
),

path(
    "admin/ranked-candidates/",
    RankedCandidatesAPI.as_view()
),


]