from django.urls import path
from .views import JobListAPI, JobCreateAPI, UserTestAPI

urlpatterns = [
    path('jobs/', JobListAPI.as_view()),
    path('jobs/create/', JobCreateAPI.as_view()),
    path('user/', UserTestAPI.as_view()),
]