"""
URL configuration for lelifeproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Sigin url  =========================================
    path('login', views.login_view, name='login_view'),
    path('register', views.register_view, name='register_view'),

    # Homeppage url  =========================================
    path('', views.homepage_view, name='homepage_view'),
    path('homepage', views.new_homepage_view, name='new_homepage'),
    
    path('our-service', views.our_service_view, name='our_service'),
    path('about-us', views.about_us_view, name='about_us'),
    path('career', views.career_view, name='career_view'),
    path('contact-us', views.contact_us_view, name='contact_us'),

    
    path('privacy-policy', views.privacy_policy_view, name='privacy_policy'),
    path('refund-policy', views.refund_policy_view, name='refund_policy'),
    path('term-condition', views.term_condition_view, name='term_condition'),
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urls.py
# For development only. In production, use a web server like Nginx to serve media files.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Only serve static files when DEBUG is True
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
