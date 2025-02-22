from django.contrib import admin
from .models import Idea

# Register your models here.


class IdeaAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "created_at", "visibility"]


admin.site.register(Idea, IdeaAdmin)
