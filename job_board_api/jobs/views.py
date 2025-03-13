import tempfile
from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import (
    JobCategorySerializer, JobPostApplicationsSerializer, JobPostSerializer,
    RegisterSerializer, UserProfileSerializer, JobApplicationSerializer, UserApplicationSerializer
)
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .filters import JobPostFilter
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.http import FileResponse, HttpResponse, HttpResponseNotFound
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import reverse
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth import get_user_model
from .tokens import account_activation_token
from datetime import datetime
import os
from .models import JobCategory, JobPost, JobApplication
from ftpretty import ftpretty
from django.conf import settings
from dotenv import load_dotenv
import logging
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView

# Create your views here.

User = get_user_model()

@api_view(['GET'])
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return Response({'message': 'Account activated successfully.'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Activation link is invalid!'}, status=status.HTTP_400_BAD_REQUEST)

def send_test_email(request):
    subject = 'Test Email'
    message = 'This is a test email sent from Django.'
    from_email = 'ivhuourpride@gmail.com'
    recipient_list = ['mwanza.n.m@gmail.com']
    
    send_mail(subject, message, from_email, recipient_list)
    
    return HttpResponse('Email sent successfully!')

def home(request):
    return render(request, 'home.html')

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            user = serializer.save()
            user.is_active = False
            user.save()

            # Generate token
            token = account_activation_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Use frontend URL from the request data
            frontend_url = request.data.get('frontendUrl')
            activation_link = f"{frontend_url}/{uid}/{token}"

            # Render email template
            email_subject = 'Activate Your Job Board Account'
            email_body = render_to_string('activation_email.html', {
                'user': user,
                'activation_link': activation_link,
                'year': datetime.now().year
            })

            # Send activation email
            send_mail(
                email_subject,
                email_body,
                os.getenv('EMAIL_HOST_USER'),
                [user.email],
                fail_silently=False,
                html_message=email_body
            )

            return Response({
                'uid': uid,
                'token': token,
                'activation_link': activation_link,
                'message': 'User registered successfully. Please check your email to activate your account.'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

logger = logging.getLogger(__name__)

class ApplyJobView(generics.CreateAPIView):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('job_post_id', openapi.IN_FORM, type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('cover_letter', openapi.IN_FORM, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('cv', openapi.IN_FORM, type=openapi.TYPE_FILE, required=True),
        ],
        responses={201: JobApplicationSerializer()},
    )
    def post(self, request, *args, **kwargs):
        job_post = get_object_or_404(JobPost, id=request.data.get('job_post_id'))
        user = request.user

        cover_letter = request.data.get('cover_letter')
        cv_file = request.FILES.get('cv')

        try:
            # Save the InMemoryUploadedFile to a temporary file
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                for chunk in cv_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name

            # Handle file upload to FTP server
            ftp = ftpretty(settings.FTP_HOST, settings.FTP_USER, settings.FTP_PASS)
            cv_path = f'{settings.FTP_DIR}/uploads/{user.username}/{cv_file.name}'
            ftp.put(tmp_file_path, cv_path)

            # Remove the temporary file
            os.remove(tmp_file_path)

            application = JobApplication.objects.create(
                user=user,
                job_post=job_post,
                cover_letter=cover_letter,
                cv_path=cv_path,
            )

            return Response(JobApplicationSerializer(application).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f'Error while applying for job: {e}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class JobCategoryViewSet(viewsets.ModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer

class JobPostViewSet(viewsets.ModelViewSet):
    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobPostFilter

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class UserApplicationsView(generics.ListAPIView):
    serializer_class = UserApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user)

class EmployerViewApplications(generics.ListAPIView):
    serializer_class = JobPostApplicationsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return JobPost.objects.all()

class DownloadCVView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'path',
                openapi.IN_QUERY,
                description="Path to the CV file",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={200: 'File Downloaded', 404: 'CV path not provided or failed to download CV'}
    )
    def get(self, request, *args, **kwargs):
        cv_path = request.query_params.get('path')
        if not cv_path:
            return HttpResponseNotFound('CV path not provided.')

        try:
            ftp = ftpretty(settings.FTP_HOST, settings.FTP_USER, settings.FTP_PASS)
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                ftp.get(cv_path, tmp_file.name)
                tmp_file_path = tmp_file.name

            response = FileResponse(open(tmp_file_path, 'rb'))
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(cv_path)}"'
            return response
        except Exception as e:
            logger.error(f'Error downloading CV: {e}')
            return HttpResponseNotFound('Failed to download CV.')
        finally:
            if os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
