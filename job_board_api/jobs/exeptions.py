from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.shortcuts import render

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return render(context['request'], '404.html', status=404)

    return response
