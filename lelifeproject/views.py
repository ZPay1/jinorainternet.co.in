# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import  redirect
# from django.contrib import messages

'''
===============================================================================================================
                            Homepage  method
===============================================================================================================
'''

def homepage_view(request):
    return render(request,'home.html')
'''
===============================================================================================================
                            Service  method
===============================================================================================================
'''

# from .models import *
# from django.shortcuts import render
# from contactus.models import Service
# def our_services_view(request):
#     services = Service.objects.filter(is_active=True, is_deleted=False).order_by('-created_at')

#     return render(request, 'our_service.html', {'services': services})






def our_service_view(request):
    return render(request,'our_service.html')    

def about_us_view(request):
    return render(request,'about_us.html')    

def career_view(request):
    return render(request,'career.html')    

def privacy_policy_view(request):
    return render(request,'privacy_policy.html')    

def refund_policy_view(request):
    return render(request,'refund_policy.html')

def term_condition_view(request):
    return render(request,'term_condition.html')

'''
===============================================================================================================
                            Contact US method
===============================================================================================================
'''

from django.shortcuts import render, redirect
from contactus.models import Contact
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import logging

def contact_us_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        print(name)
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        print(email)
        mobile = request.POST.get('mobile')
        print(mobile)
        message = request.POST.get('message')
        print(message)

        # Save to database
        Contact.objects.create(
            name=name,
            email=email,
            mobile=mobile,
            last_name=last_name,
            message=message,
        )
        
        try:
            send_mail(
                subject="Thank You for Contacting Us",
                message=f"Hi {name},\n\nThank you for reaching out. We have received your message and will get back to you shortly.\n\nRegards,\nTeam",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            print("send mail")
        except Exception as e:
             print(f'{e=}')
             pass #  (f"Error sending confirmation email: {e}")

        messages.success(request, 'Your message has been submitted.')
        return redirect('contact_us')

    return render(request, 'contact_us.html')


'''
===============================================================================================================
                            Contact US method
===============================================================================================================
'''

def register_view(request):
    return render(request, 'register.html')



def login_view(request):
    return render(request, 'login.html')


    