from django.db import models
import pycountry
import uuid

# Ye function India ke saare states fetch karega
def get_indian_state_choices():
    return [(s.name, s.name) for s in pycountry.subdivisions.get(country_code='IN')]


# ---- State Model ----
class State(models.Model):
    STATE_CHOICES = get_indian_state_choices()   # India ke states automatic milenge

    name = models.CharField(
        max_length=100,
        choices=STATE_CHOICES,
        unique=True
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = "States"

    def __str__(self):
        return self.name


# ---- Service Model ----
class Service(models.Model):

    SERVICE_CHOICES = [
        ('mobile_prepaid', 'Mobile Prepaid'),
        ('mobile_postpaid', 'Mobile Postpaid'),
        ('dth', 'DTH'),
        ('fastag', 'FasTag'),
        ('electricity_bill', 'Electricity Bill'),
        ('prepaid_meter', 'Prepaid Meter'),
        ('education', 'Education'),
        ('water', 'Water'),
        ('lpg_book_gas', 'LPG Book Gas'),
        ('rental', 'Rental'),
        ('landline_postpaid', 'Landline Postpaid'),
        ('cable_tv', 'Cable TV'),
        ('generic_gas', 'Generic Gas'),
        ('brosdband_postpaid', 'Broadband Postpaid'),
        ('insurance', 'Insurance'),
        ('municiple_taxes', 'Municipal Taxes'),
        ('subscription', 'Subscription'),
        ('club_association', 'Club Association'),
        ('donation', 'Donation'),
        ('ev_recharge', 'EV Recharge'),
        ('housing_society', 'Housing Society'),
        ('recurring_deposit', 'Recurring Deposit'),
        ('credit_card', 'Credit Card'),
        ('e_challan', 'eChallan'),
        ('loan_repayment', 'Loan Repayment'),
        ('national_pension_system', 'National Pension System'),
        ('prepaid_meter', 'Prepaid Meter'),
        ('ncmc_recharge', 'NCMC Recharge'),
        ('fleet_card_recharge', 'Fleet Card Recharge'),
        ('agent_collection', 'Agent Collection'),
    ]

    service_type = models.CharField(
        max_length=50,
        choices=SERVICE_CHOICES,
      
    )

    related_state = models.ForeignKey(
        State,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Optional: Assign service to a specific state"
    )
    rechargers_number = models.CharField(max_length=15,blank=True, null=True)
    is_active = models.BooleanField(default=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    refrence = models.CharField(max_length=55,blank=True, null=True)

    # --- NEW: Add orderid field, auto-generate value ---
    orderid = models.CharField(
        max_length=36,
        unique=True,
        editable=False,
        blank=True,
        null=False,
        default=uuid.uuid4
    )
    
    fees = models.IntegerField(null=True, blank=True)
    total_amount = models.IntegerField(null=True, blank=True)
    user_detail = models.CharField(max_length=100, blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return dict(self.SERVICE_CHOICES).get(self.service_type, self.service_type)
