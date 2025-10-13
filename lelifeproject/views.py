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

    
# def new_homepage_view(request):
#     return render(request,'homepage.html')
def new_homepage_view(request):
    if 'user_data' not in request.session: 
        return redirect('login_view') 
      

    # admin_id = request.session['admin_id']
    user_data = request.session.get('user_data', {})
    return render(request,'service_dashboard.html',{'user_data':user_data})


'''
===============================================================================================================
                            Login Method
===============================================================================================================
'''
Baseurl = "https://api.jinora.co.in/api"
from django.views.decorators.csrf import csrf_exempt
import requests

@csrf_exempt
def login_view(request):

    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '').strip()
        tpin = request.POST.get('tpin', '').strip()
        remember_me = request.POST.get('remember_me')

        # Create a session to maintain cookies
        session = requests.Session()

        # Step 2: Prepare headers and payload for login
        headers = {
            "Content-Type": "application/json",
            # "X-CSRFToken": csrf_token,
            "Referer": "https://api.jinora.co.in/api"
        }

        payload = {
            'identifier': identifier,
            'password': password,      
        }

        try:
            # Step 3: POST login request
            response = session.post(f"{Baseurl}/user/login/", json=payload, headers=headers, verify=False)
            data = response.json()
            # print(f'==========================={data=}')

            if data.get('status') == 'success':
                # Save user info and access token in session
                request.session['access_token'] = data.get('access')
      
                request.session['user_data'] = data

                if remember_me:
                    request.session.set_expiry(7 * 24 * 60 * 60)  # 7 days
                    request.session['refresh_token'] = data.get('refresh')
                else:
                    request.session.set_expiry(0)  # expires on browser close

                return redirect('new_homepage')
            else:
                messages.error(request, data.get('message', 'Login failed'))

        except requests.exceptions.RequestException as e:
            messages.error(request, f"API request failed: {str(e)}")
        except ValueError:
            messages.error(request, "Invalid response from login API.")

    return render(request, 'login.html')


'''
===============================================================================================================
                            Register Method
===============================================================================================================
'''

def register_view(request):
    message = None  


        # ✅ Common data fields
    data = {
            'username': request.POST.get('username', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'mobile': request.POST.get('mobile', '').strip(),
            'tpin': request.POST.get('tpin', '').strip(),
            'pincode': request.POST.get('pincode', '').strip(),
            'password': request.POST.get('password', '').strip(),
            'confirm_password': request.POST.get('confirm_password', '').strip(),
    }
    #print(f'{data=}')

    try:
            

            response = requests.post(f"{Baseurl}/user/register/", json=data)
            #print(f'{response=}')
            # # ##print(f'{response.text}')

            api_response = response.json()
            #print(f'rrrrrrrrrrrrrrr{api_response=}')
            
            if api_response.get('status') is True:
                message = api_response.get('message', 'Account created successfully.')
            else:
                message = api_response.get('message', 'Failed to register.')

    except ValueError:
            message = 'Invalid response from API.'
    except requests.exceptions.RequestException as e:
            message = f'API request failed: {str(e)}'

    return render(request, 'register.html', { 'message': message})


import requests
from django.shortcuts import render

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
        #print(name)
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        #print(email)
        mobile = request.POST.get('mobile')
        #print(mobile)
        message = request.POST.get('message')
        #print(message)

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
            #print("send mail")
        except Exception as e:
             #print(f'{e=}')
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


