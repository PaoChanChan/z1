from django.contrib import admin
from .models import FollowRequest

# Register your models here.


class FollowRequestAdmin(admin.ModelAdmin):
    list_display = ["from_user", "to_user", "status"]


admin.site.register(FollowRequest, FollowRequestAdmin)
