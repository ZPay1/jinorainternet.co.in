# app/models.py
from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} {self.last_name} - {self.email}"


'''
===============================================================================================================
                            Service US method
===============================================================================================================
'''

class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="service/", help_text="Upload gallery image")
    icon_image = models.ImageField(upload_to='service', help_text="Upload gallery image")
    is_active = models.BooleanField(default=True, help_text="Set True to show this service")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, blank=True, null=True)
 
