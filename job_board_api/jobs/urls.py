from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import views as auth_views
from .views import ApplyJobView, DownloadCVView, EmployerViewApplications, JobCategoryViewSet, JobPostViewSet, RegisterView, UserApplicationsView, UserProfileView, send_test_email, activate

router = DefaultRouter()
router.register(r'categories', JobCategoryViewSet)
router.register(r'jobs', JobPostViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='auth_register'),
    path('auth/profile/', UserProfileView.as_view(), name='user_profile'),
    path('send-email/', send_test_email, name='send_email'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html',email_template_name='password_reset_email.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('apply/', ApplyJobView.as_view(), name='apply_job'),
    path('user/applications/', UserApplicationsView.as_view(), name='user_applications'),
    path('employer/applications/', EmployerViewApplications.as_view(), name='employer_applications'),
    path('download_cv/', DownloadCVView.as_view(), name='download_cv'),
]