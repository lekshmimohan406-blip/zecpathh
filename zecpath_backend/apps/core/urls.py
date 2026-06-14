from django.urls import path
# from .views import JobListAPI, JobCreateAPI, UserTestAPI
from .views import (JobListAPI,JobCreateAPI,UserTestAPI,SignupAPI,LoginAPI, ProtectedAPI
)
urlpatterns = [
    path('jobs/', JobListAPI.as_view()),
    path('jobs/create/', JobCreateAPI.as_view()),
    path('user/', UserTestAPI.as_view()),

    path("signup/", SignupAPI.as_view()),
    path("login/", LoginAPI.as_view()),
    path("protected/", ProtectedAPI.as_view()),
]