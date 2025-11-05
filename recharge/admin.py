from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Service
from .models import State



@admin.register(State)
class ProductAdmin(admin.ModelAdmin):
   
    list_display = [field.name for field in State._meta.fields]

@admin.register(Service)
class ProductAdmin(admin.ModelAdmin):
   
    list_display = [field.name for field in Service._meta.fields]