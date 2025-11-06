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
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('recharge/', include('recharge.urls')),  # recharge app ke URLs include kiye

    
    # Sigin url  =========================================
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register_view'),
    path('logout/',views.logout_view, name='logout'),
    # path("download-test-pdf/", views.download_test_pdf, name="download_test_pdf"),
    # path("forgot-password/",views.forgot_password_view, name="forgot_password"),

    # Dashboard url  =========================================
    path('dashboard/', views.dashboard_view, name='dashboard_view'),
    path('pay-bill/', views.pay_bill_view, name='pay_bill'),

    
    
    path('transaction-search/', views.transaction_search_view, name='transaction_search'),
    path('receipt/', views.receipt_view, name='receipt'),
    path('complaint/', views.complaint_view, name='complaint_view'),

   # Profile url  =========================================
    path('profile/', views.profile_view, name='profile_view'),
    path('bills/', views.bills_form_view, name='bills_form'),
    path('fetch-bills/', views.fetch_bill_view, name='fetch_bill'),
    path('raise-complain/', views.raise_complain_view, name='raise_complain'),
    path('check-complaint-status/', views.check_complaint_status, name='check_complaint_status'),
    path('query-transaction/', views.query_transaction, name='query_transaction'),
    

    # path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    
    

    # Homeppage url  =========================================
    path('', views.homepage_view, name='homepage_view'),
    path('our-service/', views.our_service_view, name='our_service'),
    path('about-us/', views.about_us_view, name='about_us'),
    path('career/', views.career_view, name='career_view'),
    path('contact-us/', views.contact_us_view, name='contact_us'),

    
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('refund-policy/', views.refund_policy_view, name='refund_policy'),
    path('term-condition/', views.term_condition_view, name='term_condition'),
    
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urls.py
# For development only. In production, use a web server like Nginx to serve media files.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# Only serve static files when DEBUG is True
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
