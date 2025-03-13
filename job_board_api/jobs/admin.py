from django.contrib import admin
from .models import JobCategory, JobPost, JobApplication

# Register your models here.
admin.site.register(JobCategory)
admin.site.register(JobPost)
admin.site.register(JobApplication)