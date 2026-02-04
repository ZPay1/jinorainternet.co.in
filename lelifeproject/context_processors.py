# from django.shortcuts import render
# from django.http import HttpResponse
# import requests

# # myapp/context_processors.py
# from django.conf import settings


from django.conf import settings
def api_base_url(request):
    return {
        "API_BASE_URL": settings.JINORA_BASE_URL
    }
