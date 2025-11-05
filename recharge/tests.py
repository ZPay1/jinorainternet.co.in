
import pycountry
import uuid
from django.db import models
# Ye function India ke saare states fetch karega
def get_indian_state_choices():
    states_list = [(s.name, s.name) for s in pycountry.subdivisions.get(country_code='IN')]
    print("Fetched Indian states:", states_list)   # Print statement as requested
    return states_list


# ---- State Model ----
class State(models.Model):
    STATE_CHOICES = get_indian_state_choices()   # India ke states automatic milenge

    print("In State Model, STATE_CHOICES:", STATE_CHOICES)  # Print statement added

    name = models.CharField(
        max_length=100,
        choices=STATE_CHOICES,
        unique=True
    )

'''
https://jinorainternet.co.in/admin

Usernmae:      Jinorainternet
Email address: jinorainternet@gmail.com
Password :     jinorainternet@12    '''