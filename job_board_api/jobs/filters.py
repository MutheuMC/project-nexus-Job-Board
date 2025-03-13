from django_filters import rest_framework as filters
from .models import JobPost

class JobPostFilter(filters.FilterSet):
    title = filters.CharFilter(field_name="title", lookup_expr='icontains')
    category = filters.CharFilter(field_name="category__name", lookup_expr='icontains')
    location = filters.CharFilter(field_name="location", lookup_expr='icontains')
    experience_level = filters.CharFilter(field_name="experience_level", lookup_expr='icontains')
    created_by = filters.NumberFilter(field_name="created_by__id") 

    class Meta:
        model = JobPost
        fields = ['title', 'category', 'created_by','location','experience_level']
