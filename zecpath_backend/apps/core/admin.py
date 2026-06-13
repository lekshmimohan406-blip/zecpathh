from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "email",
        "role",
        "is_active",
        "is_verified"
    )

    list_filter = (
        "role",
        "is_active",
        "is_verified"
    )

    search_fields = (
        "email",
    )