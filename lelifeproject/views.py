# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import  redirect
# from django.contrib import messages
Baseurl = "https://api.jinora.co.in/api"
from django.views.decorators.csrf import csrf_exempt
import requests



'''===================== user login with email ===================================================='''



# Generate key only once and keep in Django settings
# settings.SECRET_KEY_FOR_ENCRYPTION = base64.urlsafe_b64encode(os.urandom(32)).decode()

def encrypt_data(data):
    f = Fernet(settings.SECRET_KEY_FOR_ENCRYPTION.encode())
    return f.encrypt(data.encode()).decode()

def decrypt_data(data):
    f = Fernet(settings.SECRET_KEY_FOR_ENCRYPTION.encode())
    return f.decrypt(data.encode()).decode()

'''
===============================================================================================================
                          Google login Method
===============================================================================================================
'''

def google_login(request):
    #print('google_login method calledd............')
    # Check if 'state' parameter is passed, otherwise default to 'login'
    state = request.GET.get('state', 'login')  # 'login' default state
    #print(f'{state=}')
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        #print(f'{identifier=}')
        password = request.POST.get('password', '').strip()
        #print(f'{password=}')
        remember_me = request.POST.get('remember_me')
        #print(f'{remember_me=}')

        # ✅ Encrypt & save in session instead of URL
        encrypted_identifier = encrypt_data(identifier)
        #print(f'{encrypted_identifier}')
        encrypted_password = encrypt_data(password)
        #print(f'{encrypted_password}')


        request.session['google_login_temp'] = {
            'identifier': encrypted_identifier,
            'password': encrypted_password,
            'remember_me': remember_me,
        }

        google_auth_url = (
            'https://accounts.google.com/o/oauth2/v2/auth'
            f'?response_type=code'
            f'&client_id={settings.GOOGLE_CLIENT_ID}'
            f'&redirect_uri={settings.GOOGLE_REDIRECT_URI_LOGIN}'
            f'&scope=profile email'
            f'&access_type=offline'
            f'&state={state}'  # Pass state parameter here
        )
        return redirect(google_auth_url)
    return redirect('sign_in')    


'''
===============================================================================================================
                          Google callback Method
===============================================================================================================
'''

def google_callback(request):
    #print('google_callback method calledd')
    code = request.GET.get('code')
    #print(f'=================={code=}')
    state = request.GET.get('state', 'login')  # Default to 'login' if state is not provided
    #print(f'{state=}')
    
    # 👇 Ye line poora current URL (including domain + query params) #print karegi
    full_url = request.build_absolute_uri()
    #print(f"Current full callback URL: {full_url}")

    # Agar sirf base path (domain + path, without query params) chahiye:
    base_path = request.build_absolute_uri(request.path)
    #print(f"Base path only: {base_path}")
    
    if not code:
        messages.error(request, 'Authorization code not received')
        return redirect('sign_in')

    # Authorization code ko tokens mein convert karna
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI_LOGIN,
        'grant_type': 'authorization_code',
    }
    token_r = requests.post(token_url, data=token_data)
    token_info = token_r.json()
    access_token = token_info.get('access_token')

    if not access_token:
        messages.error(request, 'Failed to get access token')
        return redirect('sign_in')

    # User information fetch karna
    user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
    user_info_params = {'access_token': access_token}
    user_info_r = requests.get(user_info_url, params=user_info_params)
    user_info = user_info_r.json()

    email = user_info.get('email')
    name = user_info.get('name')
    #print(f'{email}')
    #print(f'{name=}')
    if not email:
        messages.error(request, 'Failed to get user info')
        return redirect('sign_in')

    if state == 'login':   
        # Retrieve encrypted data from session
        temp_data = request.session.get('google_login_temp')
        # #print(f'{temp_data=}') 
        if not temp_data:
            messages.error(request, "Session expired or invalid.")
            return redirect('sign_in')

        identifier = decrypt_data(temp_data['identifier'])
        password = decrypt_data(temp_data['password'])
        remember_me = temp_data.get('remember_me')

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
            'email':email
         
        }
        #print(f'{payload=}')

        try:
            # Step 3: POST login request
            response = session.post(f"{Baseurl}/user/login/", json=payload, headers=headers, verify=False)
            #print(f'{response=}')
            data = response.json()
            #print(f'{data=}')

            if data.get('status') == 'success':
                # Save user info and access token in session
                request.session['access_token'] = data.get('access')
      
                request.session['user_data'] = data

                if remember_me:
                    request.session.set_expiry(7 * 24 * 60 * 60)  # 7 days
                    request.session['refresh_token'] = data.get('refresh')
                else:
                    request.session.set_expiry(0)  # expires on browser close

                if 'google_login_temp' in request.session:
                    del request.session['google_login_temp']    

                return redirect('dashboard_view')
            else:
                messages.error(request, data.get('message', 'Login failed'))
                return redirect('sign_in')

        except requests.exceptions.RequestException as e:
            messages.error(request, f"API request failed: {str(e)}")
            return redirect('sign_in')
        except ValueError:
            messages.error(request, "Invalid response from login API.")
            return redirect('sign_in')
    elif state == 'register':   
        register_data = request.session.get('register_data')

        if register_data["email"] != email:
            messages.error(request, "Email verification failed: The email you entered does not match the registered email.")
            return redirect('sign_in')

        sponsor = register_data.get('sponsor')
        data = register_data  

        try:
            if sponsor:
                url = f"{Baseurl}/register-user/"
            else:
                url = f"{Baseurl}/user/register/"

            response = requests.post(url, json=data)
            api_response = response.json()

            #print("API RAW RESPONSE:", api_response)

            if api_response.get("status") != "success":
                messages.error(request, api_response.get("message", "Registration failed"))
                return redirect('sign_in')

            user_data = api_response.get("data", {})
            #print(f'{user_data=}')

            user_raw = user_data.get("user", {})
            sponsor_raw = user_data.get("sponsor", {})

            user_info = {
                "user_id": user_raw.get("User ID"),
                "name": user_raw.get("User Name"),
                "email": user_raw.get("Email ID"),
                "mobile": user_raw.get("Mobile"),
                "password": user_raw.get("Password"),
                "registration_date": user_raw.get("Registration Date"),
            }

            sponsor_info = {
                "sponsor_id": sponsor_raw.get("Sponsor ID"),
                "sponsor_name": sponsor_raw.get("Sponsor Name"),
                "sponsor_mobile": sponsor_raw.get("Sponsor Mobile"),
            }

            message = api_response.get("message", "Account created successfully")
            # return redirect('sign_in')
            # Popup message
            request.session["popup_message"] = message
            messages.success(request, message)

            if 'register_data' in request.session:
                del request.session['register_data']

            return render(request, 'service/register.html', {
                'user_info': user_info,
                'sponsor_info': sponsor_info,
                'message': message,
                "show_popup": True,
            })

        except Exception as e:
            messages.error(request, f"API request failed: {str(e)}")
            return redirect('sign_in')

   


   
def register_account(request):
    state = "register" #request.GET.get('state', 'login')  # 'login' default state

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

        request.session['register_data'] = data

        google_auth_url = (
            'https://accounts.google.com/o/oauth2/v2/auth'
            f'?response_type=code'
            f'&client_id={settings.GOOGLE_CLIENT_ID}'
            f'&redirect_uri={settings.GOOGLE_REDIRECT_URI_LOGIN}'
            f'&scope=profile email'
            f'&access_type=offline'
            f'&state={state}'  # Pass state parameter here
        )
        return redirect(google_auth_url)
    return redirect('sign_in')            
'''
===============================================================================================================
                            login Method
===============================================================================================================
'''



def get_csrf_token(session):
    try:
        response = session.get(f"{Baseurl}/get-csrf-token/", verify=True)  
        response.raise_for_status()
        data = response.json()
        return data.get("csrfToken")
    except requests.exceptions.RequestException as e:
        # # ##print(f"Error fetching CSRF token: {e}")
        return None
    except ValueError:
        # # ##print("Invalid JSON response when fetching CSRF token")
        return None



from django.shortcuts import redirect
from django.conf import settings
from cryptography.fernet import Fernet
import base64


@csrf_exempt
def sign_in_view(request):
    #print('sign_in_view method calledddd')
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '').strip()
        remember_me = request.POST.get('remember_me')
        remember_me = request.POST.get('remember_me')
        email = request.POST.get('email')

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
            'email':email
         
        }
        # #print(f'==============={payload=}')
        try:
            # Step 3: POST login request
            response = session.post(f"{Baseurl}/user/login/", json=payload, headers=headers, verify=False)
            #print(f'{response=}')
            data = response.json()
            ##print(f'{data=}')

            if data.get('status') == 'success':
                #print(f'{data=}')
                # Save user info and access token in session
                request.session['access_token'] = data.get('access')
                request.session['refresh_token'] = data.get('refresh')  # ✅ ALWAYS SAVE
      
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

    return render(request, 'service/login.html', {'form_type': 'signin'})


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
            api_response = response.json()
            # #print(f'{api_response=}')
            if api_response.get('status') is True:
              
                message = api_response.get('message', 'Account created successfully.')
                return redirect('sign_in')
            else:
                message = api_response.get('message', 'Failed to register.')
                # #print(f'{message=}')
        except ValueError:
            message = 'Invalid response from API.'
        except requests.exceptions.RequestException as e:
            message = f'API request failed: {str(e)}'


    return render(request, 'service/register.html',{ 'msg': message})


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
        return redirect('sign_in') 
      
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
    #print('profile method called')
    if 'user_data' not in request.session: 
        return redirect('sign_in') 

    access_token = request.session.get('access_token')
    user_data = request.session.get("user_data") 
    # cart_count = request.session.get("cart_count")

    if not access_token:
        return redirect('sign_in')

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
            return redirect('sign_in')

    try:
        if response.status_code == 200:
            response.raise_for_status()
            profile_data = response.json().get('data', {})
            #print(f'{profile_data=}')
          
           
  
            return render(request, 'service/profile.html', {
                'user_data': user_data,
                'profile_data': profile_data,
                # 'cart_count': cart_count,
            })
        else:
            return redirect('sign_in')

    except requests.exceptions.RequestException:
        return render(request, 'service/profile.html', {
            'user_data': None,
            'error': 'Failed to load user details'
        })







# def recharge_form_view(request):
#     user_data = request.session.get('user_data', {})

#     return render(request,'service/recharge_form.html',{'user_data':user_data})


def pay_bill_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})

    return render(request,'service/paybill.html',{'user_data':user_data})




def transaction_search_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})

    return render(request,'service/transaction_search.html',{'user_data':user_data})


def complaint_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})

    return render(request,'service/complaint_page.html',{'user_data':user_data})


def bills_form_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})

    return render(request,'service/bill_form.html',{'user_data':user_data})



def fetch_bill_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})

    return render(request,'service/fetch_bill.html',{'user_data':user_data})







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

def recharge_page_view(request):
    return render(request,'recharge.html')



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
        ##print(name)
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        ##print(email)
        mobile = request.POST.get('mobile')
        ##print(mobile)
        message = request.POST.get('message')
        ##print(message)

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
            ##print("send mail")
        except Exception as e:
             ##print(f'{e=}')
             pass #  (f"Error sending confirmation email: {e}")

        messages.success(request, 'Your message has been submitted.')
        return redirect('contact_us')

    return render(request, 'contact_us.html')




# def register_view(request):
#     return render(request, 'register.html')


