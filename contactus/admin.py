from django.contrib import admin

from .models import Contact
from .models import Service

'''
===============================================================================================================
                            Contact Us
===============================================================================================================
'''    
@admin.register(Contact)
class COntactUsAdmin(admin.ModelAdmin):
   
    list_display = [field.name for field in Contact._meta.fields]
'''
===============================================================================================================
                            Service 
===============================================================================================================
'''    
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
   
    list_display = [field.name for field in Service._meta.fields]