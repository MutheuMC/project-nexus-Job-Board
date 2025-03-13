from django.core.management.base import BaseCommand
from jobs.models import JobCategory, JobPost
from django.contrib.auth.models import User
import random

class Command(BaseCommand):
    help = 'Seed database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')
        self.seed_categories()
        self.seed_jobs()
        self.stdout.write('Database seeded successfully.')

    def seed_categories(self):
        categories = ['Engineering', 'Marketing', 'Finance', 'Sales', 'Human Resources']
        for category_name in categories:
            JobCategory.objects.get_or_create(name=category_name)
        self.stdout.write('Job categories seeded.')

    def seed_jobs(self):
        user = User.objects.first()  # Get the first user
        categories = JobCategory.objects.all()
        experience_levels = ['Entry', 'Mid', 'Senior']
        job_titles = [
            'Software Engineer', 'Marketing Specialist', 'Financial Analyst', 
            'Sales Manager', 'HR Coordinator', 'Data Scientist', 
            'UX Designer', 'Project Manager', 'Content Writer', 'Customer Support'
        ]
        locations = [
            'New York, NY', 'San Francisco, CA', 'Chicago, IL', 
            'Los Angeles, CA', 'Austin, TX', 'Boston, MA', 
            'Seattle, WA', 'Denver, CO', 'Atlanta, GA', 'Miami, FL'
        ]
        companies = ['Acme Corp', 'Stark Enterprises', 'Wayne Enterprises', 
                     'Oscorp Industries', 'Pied Piper', 'Hooli']

        for i in range(20):
            job_post = JobPost(
                title=random.choice(job_titles),
                description='This is a sample job description.',
                location=random.choice(locations),
                company_name=random.choice(companies),
                category=random.choice(categories),
                created_by=user,
                experience_level=random.choice(experience_levels)
            )
            job_post.save()
        self.stdout.write('Job posts seeded.')
