
# from django.contrib import admin
# from django.urls import path
# from . import views
# # Recharge pages url  =========================================
# path('mobile-prepaid/', views.mobile_prepaid_view, name='mobile_prepaid'),

from django.urls import path

from recharge import views_mobile_prepaid,views_rental,views_cable_tv,views_health_insurance
from . import views,views_fastag ,views_electricity_bill ,views_gas_bill,views_loan_repayment_bill,views_education_fees,views_insurance,views_water,views_landline_postpaid,views_hospital,views_municiple_taxes

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


        
    # =================== Electriv Bill URLS ===================
    path("electricity/bill", views_electricity_bill.electricity_category_view, name="electricity_category"),
    path("electricity/fetch/", views_electricity_bill.electricity_fetch_bill, name="electricity_fetch"),
    path("electricity/confirm/", views_electricity_bill.electricity_confirm, name="electricity_confirm"),
    path("electricity/payment/", views_electricity_bill.electricity_payment, name="electricity_payment"),
    
  # =================== Gas Bill URLS ===================
    path("gas/bill", views_gas_bill.gas_category_view, name="gas_category"),
    path("gas/fetch/", views_gas_bill.gas_fetch_bill, name="gas_fetch"),
    path("gas/confirm/", views_gas_bill.gas_bill_confirm, name="gas_bill_confirm"),
    path("gas/payment/", views_gas_bill.gas_bill_payment, name="gas_bill_payment"),

  # =================== Loan Bill URLS ===================
    path("loan/repayment", views_loan_repayment_bill.loan_category_view, name="loan_category"),
    path("loan/repayment/fetch/", views_loan_repayment_bill.loan_fetch_bill, name="loan_fetch"),
    path("loan/repayment/confirm/", views_loan_repayment_bill.loan_bill_confirm, name="loan_confirm"),
    path("loan/repayment/payment/", views_loan_repayment_bill.loan_bill_payment, name="loan_payment"),
    
  # =================== Education Fees Bill URLS ===================
    path("education/fees/bill", views_education_fees.education_fees_category_view, name="education_category"),
    path("education/fees/bill/fetch/", views_education_fees.education_fees_fetch_bill, name="education_fetch"),
    path("education/fees/bill/confirm/", views_education_fees.education_fees_bill_confirm, name="education_confirm"),
    path("education/fees/bill/payment/", views_education_fees.education_fees_payment, name="education_payment"),
    

  # =================== Insurance Bill URLS ===================
    path("Insurance/bill", views_insurance.insurance_category_view, name="insurance_category"),
    path("Insurance/bill/fetch/", views_insurance.insurance_fetch_bill, name="insurance_fetch"),
    path("Insurance/bill/confirm/", views_insurance.insurance_bill_confirm, name="insurance_confirm"),
    path("Insurance/bill/payment/", views_insurance.insurance_payment, name="insurance_payment"),
    

 # =================== Water Bill URLS ===================
    path("water/bill", views_water.water_category_view, name="water_category"),
    path("water/bill/fetch/", views_water.water_fetch_bill, name="water_fetch"),
    path("water/bill/confirm/", views_water.water_bill_confirm, name="water_confirm"),
    path("water/bill/payment/", views_water.water_payment, name="water_payment"),

 # =================== Landline Postpaid Bill URLS ===================
    path("landline/bill", views_landline_postpaid.landline_postpaid_category_view, name="landline_postpaid_category"),
    path("landline/bill/fetch/", views_landline_postpaid.landline_postpaid_fetch_bill, name="landline_postpaid_fetch"),
    path("landline/bill/confirm/", views_landline_postpaid.landline_postpaid_bill_confirm, name="landline_postpaid_confirm"),
    path("landline/bill/payment/", views_landline_postpaid.landline_postpaid_payment, name="landline_postpaid_payment"),


 # =================== Rental Bill URLS ===================
    path("rental/bill", views_rental.rental_category_view, name="rental_category"),
    path("rental/bill/fetch/", views_rental.rental_fetch_bill, name="rental_fetch"),
    path("rental/bill/confirm/", views_rental.rental_bill_confirm, name="rental_confirm"),
    path("rental/bill/payment/", views_rental.rental_bill_payment, name="rental_payment"),


 # =================== Cable TV Bill URLS ===================
    path("cable-tv/bill", views_cable_tv.cable_tv_category_view, name="cable_tv_category"),
    path("cable-tv/bill/fetch/", views_cable_tv.cable_tv_fetch_bill, name="cable_tv_fetch"),
    path("cable-tv/bill/confirm/", views_cable_tv.cable_tv_bill_confirm, name="cable_tv_confirm"),
    path("cable-tv/bill/payment/", views_cable_tv.cable_tv_bill_payment, name="cable_tv_payment"),

 # =================== Hospital Bill URLS ===================
    path("hospital/bill", views_hospital.hospital_category_view, name="hospital_category"),
    path("hospital/bill/fetch/", views_hospital.hospital_fetch_bill, name="hospital_fetch"),
    path("hospital/bill/confirm/", views_hospital.hospital_bill_confirm, name="hospital_confirm"),
    path("hospital/bill/payment/", views_hospital.hospital_bill_payment, name="hospital_payment"),


 # =================== Health Insurance Bill URLS ===================
    path("health-insurance/bill", views_health_insurance.health_insurance_category_view, name="health_insurance_category"),
    path("health-insurance/bill/fetch/", views_health_insurance.health_insurance_fetch_bill, name="health_insurance_fetch"),
    path("health-insurance/bill/confirm/", views_health_insurance.health_insurance_bill_confirm, name="health_insurance_confirm"),
    path("health-insurance/bill/payment/", views_health_insurance.health_insurance_bill_payment, name="health_insurance_payment"),


 # =================== Municiple Taxes Bill URLS ===================
    path("municiple-taxes/bill", views_municiple_taxes.municiple_taxes_category_view, name="municiple_taxes_category"),
    path("municiple-taxes/bill/fetch/", views_municiple_taxes.municiple_taxes_fetch_bill, name="municiple_taxes_fetch"),
    path("municiple-taxes/bill/confirm/", views_municiple_taxes.municiple_taxes_bill_confirm, name="municiple_taxes_confirm"),
    path("municiple-taxes/bill/payment/", views_municiple_taxes.municiple_taxes_bill_payment, name="municiple_taxes_payment"),


    # =================== Mobile Prepaid RECHARGE URLS ===================
    path("mobile-prepaid/", views_mobile_prepaid.mobile_prepaid_category_view, name="mobile_prepaid_category"),
    path("mobile-prepaid/plans/",views_mobile_prepaid.mobile_prepaid_plans_view, name="mobile_prepaid_plans"),
    path("mobile-prepaid/validate/", views_mobile_prepaid.mobile_prepaid_validate_view, name="mobile_prepaid_fetch"),
    path("mobile-prepaid/confirm/", views_mobile_prepaid.mobile_prepaid_confirm, name="mobile_prepaid_confirm"),
    path("mobile-prepaid/payment/", views_mobile_prepaid.mobile_prepaid_payment, name="mobile_prepaid_payment"),
    # path("success/", views.recharge_success, name="recharge_success"),



  # ===================  Navbar RECHARGE URLS ===================
    path('transaction-hisotry/', views.transaction_history_view, name='transaction_hisotry'),
    path('transaction-status/', views.check_transaction_status, name='check_transaction_status'),
   
    # 🔹 NPCI complaint (GET = form + dispositions, POST = raise complaint)
    path(
        "raise-complaint/",views.
        raise_npci_complaint,
        name="raise_npci_complaint"
    ),  
    path('not-found/', views.not_found_page, name='not_found_page'),
    path('complain-history/', views.complain_history_view, name='complain_history'),




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
