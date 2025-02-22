from django.contrib import admin
from .models import User, Profile

# Register your models here.


class UserAdmin(admin.ModelAdmin):
    list_display = ["full_name", "username", "email"]


class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "full_name", "country", "city", "created_at", "verified"]
    list_editable = ["verified"]


admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
