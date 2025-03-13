from django.db import models
from django.contrib.auth.models import User 

# Create your models here.
def get_default_user():
    return User.objects.first().id

class JobCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class JobPost(models.Model):
    EXPERIENCE_LEVEL_CHOICES = [
        ('Entry', 'Entry Level'),
        ('Mid', 'Mid Level'),
        ('Senior', 'Senior Level'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE)
    posted_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES)

    def __str__(self):
        return self.title

class JobApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_post = models.ForeignKey('JobPost', on_delete=models.CASCADE)
    cover_letter = models.TextField()
    cv_path = models.CharField(max_length=255)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.job_post.title}'


