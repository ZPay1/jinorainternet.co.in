
# from django.contrib import admin
# from django.urls import path
# from . import views
# # Recharge pages url  =========================================
# path('mobile-prepaid/', views.mobile_prepaid_view, name='mobile_prepaid'),

from django.urls import path
from . import views  # <-- same app ke views import karo

urlpatterns = [


    path('mobile-prepaid/', views.mobile_prepaid_view, name='mobile_prepaid'),
    # path('recharge-success/', views.recharge_success_view, name='recharge_success'),
    path('mobile-postpaid/', views.mobile_postpaid_view, name='mobile_postpaid'),
    path('dth-recharge/', views.dth_recharge_view, name='dth_recharge'),
    path('fastag-recharge/', views.fastag_recharge_view, name='fastag_recharge'),
    path('electricity-bill/', views.electricity_bill_view, name='electricity_bill'),
    path('transaction-hisotry/', views.transaction_history_view, name='transaction_hisotry'),
    path('not-found/', views.not_found_page, name='not_found_page'),
    path('complain-history/', views.complain_history_view, name='complain_history'),
    path('education/', views.education_view, name='education'),
    path('water/', views.water_view, name='water'),
    path('lpg-book-gas/', views.lpg_book_gas_view, name='lpg_book_gas'),
    path('', views.recharge_view, name='recharge_view'),

    # Footer url  =========================================
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy_view'),
    path('term-of-us/', views.term_of_us_view, name='term_of_us_view'),
    path('refund-policy/', views.refund_policy_view, name='refund_policy_view'),
    path('about-us/', views.about_us_view, name='about_us_view'),
    path('cookie-policy/', views.cookie_policy_view, name='cookie_policy_view'),
    path('team/', views.team_view, name='team_view'),
    path('career-page/', views.career_page_view, name='career_page_view'),
    path('bbps-tsp/', views.bbps_tsp_view, name='bbps_tsp_view'),
    path('receipt/', views.receipt_view, name='receipt'),
    
    path('query-transaction/', views.query_transaction, name='query_transaction'),
    path('raise-complain/', views.raise_complain_view, name='raise_complain'),
    path('check-complaint-status/', views.check_complaint_status, name='check_complaint_status'),
    
    # path('term-condition/', views.term_condition_view, name='term_condition'),
    
    
    
    
]
