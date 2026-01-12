
# from django.contrib import admin
# from django.urls import path
# from . import views
# # Recharge pages url  =========================================
# path('mobile-prepaid/', views.mobile_prepaid_view, name='mobile_prepaid'),

from django.urls import path

from recharge import views_mobile_prepaid
from . import views,views_fastag  # <-- same app ke views import karo

urlpatterns = [
    path('', views.recharge_view, name='recharge_view'),
    path('category/',views.category_view, name='category_view'),
    path('fastag-recharge/', views.fastag_recharge, name='fastag_recharge'),
    path('fastag-payment/', views.fastag_payment, name='fastag_payment'),

    
    # =================== FASTAG RECHARGE URLS ===================
    path("fastag/", views_fastag.fastag_category_view, name="fastag_category"),
    path("fastag/fetch/", views_fastag.fastag_fetch_bill, name="fastag_fetch"),
    path("fastag/confirm/", views_fastag.fastag_confirm, name="fastag_confirm"),
    path("fastag/payment/", views_fastag.fastag_payment, name="fastag_payment"),
    path("success/", views.recharge_success, name="recharge_success"),
   
    
    # =================== Mobile Prepaid RECHARGE URLS ===================
    path("mobile-prepaid/", views_mobile_prepaid.mobile_prepaid_category_view, name="mobile_prepaid_category"),
    path("mobile-prepaid/plans/",views_mobile_prepaid.mobile_prepaid_plans_view, name="mobile_prepaid_plans"),
    # path("mobile-prepaid/fetch/",views_mobile_prepaid.mobile_prepaid_fetch_view, name="mobile_prepaid_fetch"),


    path("mobile-prepaid/validate/", views_mobile_prepaid.mobile_prepaid_validate_view, name="mobile_prepaid_fetch"),
    path("mobile-prepaid/confirm/", views_mobile_prepaid.mobile_prepaid_confirm, name="mobile_prepaid_confirm"),
    path("mobile-prepaid/payment/", views_mobile_prepaid.mobile_prepaid_payment, name="mobile_prepaid_payment"),
    # path("success/", views.recharge_success, name="recharge_success"),

    path('mobile-prepaid/', views.mobile_prepaid_view, name='mobile_prepaid'),
    # path('recharge-success/', views.recharge_success_view, name='recharge_success'),
    path('mobile-postpaid/', views.mobile_postpaid_view, name='mobile_postpaid'),
    path('dth-recharge/', views.dth_recharge_view, name='dth_recharge'),
    path('electricity-bill/', views.electricity_bill_view, name='electricity_bill'),
    path('education/', views.education_view, name='education'),
    path('water/', views.water_view, name='water'),
    path('lpg-book-gas/', views.lpg_book_gas_view, name='lpg_book_gas'),
    path('rental/', views.rental_view, name='rental_view'),
    path('landline-postpaid/', views.landline_postpaid_view, name='landline_postpaid'),
    path('cable-tv/', views.cable_tv_view, name='cable_tv_view'),
    path('generic-gas/', views.generic_gas_view, name='generic_gas_view'),
    path('broadband-postpaid/', views.brosdband_postpaid_view, name='brosdband_postpaid_view'),
    path('Insurance/', views.insurance_view, name='insurance_view'),
    path('municiple-taxes/', views.municiple_taxes_view, name='municiple_taxes_view'),
    path('subscription/', views.subscription_view, name='subscription_view'),
    path('club-association/', views.club_assiciation_view, name='club_assiciation_view'),
    path('donation/', views.donation_view, name='donation_view'),
    path('ev-recharge/', views.ev_recharge_view, name='ev_recharge_view'),

    path('housing-society/', views.housing_society_view, name='housing_society_view'),
    path('municiple-services/', views.municiple_services_view, name='municiple_services_view'),
    path('recurring-deposite/', views.recurring_deposite_view, name='recurring_deposite_view'),
    path('credit-card/', views.credit_card_view, name='credit_card_view'),
    path('e-challan/', views.e_challan_view, name='e_challan_view'),
    path('loan-repayment/', views.loan_repayment_view, name='loan_repayment_view'),
    path('national-pension-system/', views.national_pension_system_view, name='national_pension_system_view'),
   
    path('prepaid-meter/', views.prepaid_meter_view, name='prepaid_meter_view'),
    path('ncmc-recharge/', views.ncmc_recharge_view, name='ncmc_recharge_view'),
    path('fleet-card-recharge/', views.fleet_card_recharge_view, name='fleet_card_recharge_view'),
    path('agent-collection/', views.agent_collection_view, name='agent_collection_view'),
   

    path('transaction-hisotry/', views.transaction_history_view, name='transaction_hisotry'),
    path('not-found/', views.not_found_page, name='not_found_page'),
    path('complain-history/', views.complain_history_view, name='complain_history'),


    # Footer url  =========================================
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy_view'),
    path('term-of-us/', views.term_of_us_view, name='term_of_us_view'),
    path('refund-policy/', views.refund_policy_view, name='refund_policy_view'),
    path('about-us/', views.about_us_view, name='about_us_view'),
    path('cookie-policy/', views.cookie_policy_view, name='cookie_policy_view'),
    path('team/', views.team_view, name='team_view'),
    path('career-page/', views.career_page_view, name='career_page_view'),
    path('bbps-tsp/', views.bbps_tsp_view, name='bbps_tsp_view'),
    path('receipt/<int:id>/', views.receipt_view, name='receipt'),
    
    path('query-transaction/', views.query_transaction, name='query_transaction'),
    path('raise-complain/', views.raise_complain_view, name='raise_complain'),
    path('check-complaint-status/', views.check_complaint_status, name='check_complaint_status'),
    path('sms-slip/', views.sms_slip_view, name='sms_slip'),
    
    
    # path('term-condition/', views.term_condition_view, name='term_condition'),
    
    
    
    
]
