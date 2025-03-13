from rest_framework import serializers
from .models import JobCategory, JobPost, JobApplication
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.models import User

class UserApplicationSerializer(serializers.ModelSerializer):
    job_post_title = serializers.CharField(source='job_post.title', read_only=True)

    class Meta:
        model = JobApplication
        fields = ['job_post_title', 'cover_letter', 'cv_path', 'submitted_at']

class ApplicantSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    cv_url = serializers.SerializerMethodField()

    class Meta:
        model = JobApplication
        fields = ['username', 'email', 'cover_letter', 'cv_url', 'submitted_at']

    def get_cv_url(self, obj):
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(f'/api/download_cv/?path={obj.cv_path}')
        return f'/api/download_cv/?path={obj.cv_path}'


class JobPostApplicationsSerializer(serializers.ModelSerializer):
    applicants = ApplicantSerializer(source='jobapplication_set', many=True, read_only=True)

    class Meta:
        model = JobPost
        fields = ['title', 'description', 'applicants']

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['user', 'job_post', 'cover_letter', 'cv_path', 'submitted_at']


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = '__all__'

class JobPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPost
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        read_only_fields = ['username']