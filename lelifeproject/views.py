# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import  redirect
# from django.contrib import messages
Baseurl = "https://api.jinora.co.in/api"
from django.views.decorators.csrf import csrf_exempt
import requests

'''
===============================================================================================================
                            Login Method
===============================================================================================================
'''



def get_csrf_token(session):
    """
    Fetch CSRF token using the same session to maintain cookies.
    """
    try:
        response = session.get(f"{Baseurl}/get-csrf-token/", verify=True)  
        response.raise_for_status()
        data = response.json()
        return data.get("csrfToken")
    except requests.exceptions.RequestException as e:
        # # #print(f"Error fetching CSRF token: {e}")
        return None
    except ValueError:
        # # #print("Invalid JSON response when fetching CSRF token")
        return None

@csrf_exempt
def login_view(request):

    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '').strip()
        # tpin = request.POST.get('tpin', '').strip()
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

                return redirect('dashboard_view')
            else:
                messages.error(request, data.get('message', 'Login failed'))

        except requests.exceptions.RequestException as e:
            messages.error(request, f"API request failed: {str(e)}")
        except ValueError:
            messages.error(request, "Invalid response from login API.")

    return render(request, 'service/login.html')



'''
===============================================================================================================
                            refresh token Method
===============================================================================================================
'''
   
def refresh_tokents(request):
    import json

    refresh_token = request.session.get('refresh_token')
    if not refresh_token:
        return False  # agar refresh token hi nahi hai to login karwana padega

    url = f"{Baseurl}/refresh-token/"
    payload = json.dumps({"refresh": refresh_token})
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, headers=headers, data=payload)
        data = response.json()
        if 'access' in data:
            # ✅ Session me naya token dal do
            request.session['access_token'] = data.get('access')
            request.session['refresh_token'] = data.get('refresh', refresh_token)
            return True  # refresh success
        return False  # refresh fail
    except Exception:
        return False

'''
===============================================================================================================
                            Register Method
===============================================================================================================
'''

def register_view(request):
   
    message = None  
    if request.method == 'POST':
    
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
        try:

            response = requests.post(f"{Baseurl}/user/register/", json=data)
            # print(f'{response=}')
            # print(f'{response.text}')

            api_response = response.json()
            # print(f'{api_response=}')
            
            if api_response.get('status') is True:
                message = api_response.get('message', 'Account created successfully.')
            else:
                message = api_response.get('message', 'Failed to register.')

        except ValueError:
                message = 'Invalid response from API.'
        except requests.exceptions.RequestException as e:
            message = f'API request failed: {str(e)}'
    # print(f'{message=}=')
    return render(request, 'service/register.html', { 'msg': message})





'''
===============================================================================================================
                      Logout Method
===============================================================================================================
'''

from django.shortcuts import redirect
from django.contrib import messages
import requests

def logout_view(request):
    # Logout API ka use kare
    try:
        # Maan lijiye ki session me token ya user_id hai, use bhejna ho sakta hai API ko
        access_token = request.session.get('access_token')
     
        headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
        # API endpoint (change Baseurl to your actual value or import from settings)
        API_LOGOUT_URL = f"{Baseurl}/user/logout/"

        # API call karein
        response = requests.post(API_LOGOUT_URL, headers=headers)
        api_result = response.json()
        if response.status_code == 200:
            # Agar API logout successful ho
            messages.success(request, api_result.get('message', 'Logged out successfully.'))
        else:
            # Agar API ne koi aur message diya ho to
            messages.warning(request, api_result.get('message', 'Logout failed.'))
    except Exception as e:
        # Exception ke case me ek generic message dikha de
        messages.error(request, f"Logout failed: {str(e)}")

    # Clear all session data
    request.session.flush()
    return redirect('homepage_view')  


'''
===============================================================================================================
                    Dashbaord Method
===============================================================================================================
'''

def dashboard_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
      
    # admin_id = request.session['admin_id']
    user_data = request.session.get('user_data', {})
    return render(request,'service/service_dashboard_new.html',{'user_data':user_data})

'''
===============================================================================================================
                    Profile Method
===============================================================================================================
'''

import requests
from django.shortcuts import render


def profile_view(request):
    print('profile method called')
    if 'user_data' not in request.session: 
        return redirect('login') 

    access_token = request.session.get('access_token')
    user_data = request.session.get("user_data") 
    # cart_count = request.session.get("cart_count")

    if not access_token:
        return redirect('login')

    def get_profile(token):
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        return requests.get(f"{Baseurl}/get-user/details/", headers=headers)

    response = get_profile(access_token)


    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get('access_token')
            response = get_profile(new_token)
        else:
            return redirect('login')

    try:
        if response.status_code == 200:
            response.raise_for_status()
            profile_data = response.json().get('data', {})
            print(f'{profile_data=}')
          
           
  
            return render(request, 'service/profile.html', {
                'user_data': user_data,
                'profile_data': profile_data,
                # 'cart_count': cart_count,
            })
        else:
            return redirect('login')

    except requests.exceptions.RequestException:
        return render(request, 'service/profile.html', {
            'user_data': None,
            'error': 'Failed to load user details'
        })







'''
===============================================================================================================
                    Forgot Password Method
===============================================================================================================
'''

from django.shortcuts import render
from django.contrib import messages
import requests


'''def forgot_password_view(request):
    if request.method == "POST":
        userid_or_mobile = request.POST.get("userid_or_mobile", "").strip()
        if not userid_or_mobile:
            messages.error(request, "User ID or Mobile is required.")
        else:
            # Call the API
            url = "https://api.jinora.co.in/forgot-password/"
            headers = {"Content-Type": "application/json"}
            payload = {"userid_or_mobile": userid_or_mobile}
            try:
                response = requests.post(url, json=payload, headers=headers)
                data = response.json()
                if data.get("status") == "success":
                    messages.success(request, data.get("message"))
                else:
                    messages.error(request, data.get("message"))
            except Exception as e:
                messages.error(request, f"Something went wrong: {str(e)}")
    return render(request, "service/forgot_password.html")  ''' 






# def recharge_form_view(request):
#     user_data = request.session.get('user_data', {})

#     return render(request,'service/recharge_form.html',{'user_data':user_data})


def pay_bill_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})

    return render(request,'service/paybill.html',{'user_data':user_data})




def transaction_search_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})

    return render(request,'service/transaction_search.html',{'user_data':user_data})

def receipt_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})

    return render(request,'service/receipt.html',{'user_data':user_data})

def complaint_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})

    return render(request,'service/complaint_page.html',{'user_data':user_data})


def bills_form_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})

    return render(request,'service/bill_form.html',{'user_data':user_data})



def fetch_bill_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})

    return render(request,'service/fetch_bill.html',{'user_data':user_data})



def raise_complain_view(request):
    user_data = request.session.get('user_data', {})

    return render(request,'service/raise_complaint_page.html',{'user_data':user_data})

def check_complaint_status(request):
    user_data = request.session.get('user_data', {})

    return render(request,'service/check_complain_status.html',{'user_data':user_data})

def query_transaction(request):
    user_data = request.session.get('user_data', {})

    return render(request,'service/query_transaction.html',{'user_data':user_data})

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





def homepage_view(request):
    return render(request,'home.html')


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

def download_test_pdf(request):
    return render(request,'service/download_test_pdf.html')


# from django.http import FileResponse
# import io
# from reportlab.pdfgen import canvas

# def download_test_pdf(request):
#     buffer = io.BytesIO()
#     p = canvas.Canvas(buffer)
#     p.drawString(100, 750, "✅ PDF Download Successful!")
#     p.showPage()
#     p.save()
#     buffer.seek(0)

#     response = FileResponse(buffer, as_attachment=True, filename="test_report.pdf")
#     response.set_cookie("fileDownload", "true", max_age=5)
#     return response

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




# def register_view(request):
#     return render(request, 'register.html')


