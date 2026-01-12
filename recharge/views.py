from urllib import request
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render
# from .models import Service
from django.shortcuts import render, redirect
from django.contrib import messages
# Create your views here.
'''
===============================================================================================================
                            Recharge Pages  method
===============================================================================================================
'''
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import  redirect
from django.shortcuts import render, redirect
from .models import Service, State

'''
===============================================================================================================
                            Recharge method
===============================================================================================================
'''

import requests
Baseurl = "https://api.jinora.co.in/api"


import requests
from django.shortcuts import render, redirect



def recharge_view(request):
    if 'user_data' not in request.session:
        return redirect('sign_in')
    user_data = request.session.get('user_data', {})
    return render(
        request,
        'recharge/recharge_page.html',
        {
            'user_data': user_data,
        
        }
    )
import requests
from django.shortcuts import render, redirect

def category_view(request):
    if 'user_data' not in request.session:
        return redirect('sign_in')

    user_data = request.session.get('user_data', {})
    access_token = user_data.get("access")  

    category = request.GET.get('category', 'Fastag')
    # print(f"{category=}")

    billers = []

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(
            f"{Baseurl}/npci/get-biller-by-category/",
            params={"category": category},
            headers=headers
        )
        # print(f"{response.status_code=}")
        # print(response.text)

        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("status") is True:
                billers = res_json.get("data", [])

    except Exception as e:
        pass
        # print("API Error:", e)

    return render(
        request,
        "recharge/category_page.html",
        {
            "user_data": user_data,
            "billers": billers,
            "category": category
        }
    )





def fastag_form(request):
    if 'user_data' not in request.session:
        return redirect('sign_in')

    user_data = request.session.get('user_data', {})
    access_token = user_data.get("access")
    
    
    billerId = request.GET.get("billerId")
    billerName = request.GET.get("billerName")

    return render(
        request,
        "recharge/fastag_recharge.html",
        {
            "billerId": billerId,
            "billerName": billerName,
            "user_data": user_data
        }
    )

import json
import requests
from django.shortcuts import render, redirect



def fastag_recharge(request):
    if 'user_data' not in request.session:
        return redirect('sign_in')

    user_data = request.session.get('user_data', {})
    access_token = user_data.get("access")
    

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    print(f"1  {user_data=}")    
    if request.method == "POST":
        vehicle_number = request.POST.get("vehicle_number")
        billerId = request.POST.get("billerId")

        payload = {
            "vehicle_number": vehicle_number,
            "billerId": billerId,
            
        }
        try:
            response = requests.post(
                f"{Baseurl}/npci/fetch-fastag-bill/",
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                res_json = response.json()
                print(f'{res_json=}')
                if res_json.get("status") is True:
                    payload = res_json["data"]["payload"]
                    print(f'======================{payload=}')
                    additional = payload.get("additionalParams", {})
                    print(f'======================={additional=}')
                    context = {
                       "user_data": user_data,
                        "vehicle_number": vehicle_number,
                        "payload": payload,
                        # 'additional':additional,
                        # "tag_status": additional.get("Tag Status"),
                        # "wallet_balance": additional.get("Wallet Balance"),
                        # "max_recharge": additional.get("Maximum Permissible Recharge Amount"),

                        # 🔑 IMPORTANT
                        "return_payload_json": json.dumps(res_json["return_payload"]),
                    }

                    return render(
                        request,
                        "recharge/fastag_recharge.html",
                        context
                    )
        except Exception as e:
            pass
    print(f"{user_data=}")        
    return render(request, "recharge/fastag_recharge.html", {
        "user_data": user_data
    })




import json
import requests



def fastag_payment(request):
    # print('ttttttttttttttt')
    if 'user_data' not in request.session:
        return redirect('sign_in')

    user_data = request.session.get('user_data', {})
    access_token = user_data.get("access")

    if request.method == "POST":
        amount = request.POST.get("amount")
        return_payload = json.loads(request.POST.get("return_payload"))

        payload = {
            "amount": amount,
            "return_payload": return_payload
        }
        print(f'{payload=}')

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            f"{Baseurl}/npci/bill-payment/",
            json=payload,
            headers=headers
        )
        print(f'{response=}')

        if response.status_code == 200:
            return render(
                request,
                "recharge/confirmation_page.html",
                {
                    "response": response.json(),
                    "user_data": user_data
                }
            )



    return render(request,"recharge/confirmation_page.html")
import json

# def fastag_payment(request):
#     if 'user_data' not in request.session:
#         return redirect('sign_in')

#     user_data = request.session.get('user_data', {})
#     access_token = user_data.get("access")

#     if request.method == "POST":
#         amount = request.POST.get("amount")
#         return_payload_raw = request.POST.get("return_payload")

#         # ✅ SAFE LOAD
#         return_payload = json.loads(return_payload_raw)

#         payload = {
#             "amount": amount,
#             "return_payload": return_payload
#         }

#         headers = {
#             "Authorization": f"Bearer {access_token}",
#             "Content-Type": "application/json"
#         }

#         response = requests.post(
#             f"{Baseurl}/npci/bill-payment/",
#             json=payload,
#             headers=headers
#         )

#         if response.status_code == 200:
#             return render(
#                 request,
#                 "recharge/confirmation_page.html",
#                 {
#                     "response": response.json(),
#                     "amount": amount
#                 }
#             )

#     return redirect("fastag_recharge")


    
'''
===============================================================================================================
                            Mobile Prepaid method
===============================================================================================================
'''

def mobile_prepaid_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
  
    userid = user_data.get('userid')
    username = user_data.get('username')
    userdt = f'{username}-({userid})'
    # print(f'{states=}')
    success_data = None
    if request.method == 'POST':
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'mobile_prepaid' #request.POST.get('service_type')
        state_id = request.POST.get('related_state')
        refrence = request.POST.get('refrence')
        amount = request.POST.get('amount')
        related_state = State.objects.filter(id=state_id).first()
        fees = 0

        # Save data to the database
        service = Service.objects.create(
            service_type=service_type,
            rechargers_number=rechargers_number,
            related_state=related_state,
            amount=amount,
            refrence = refrence,
            status='Pending',   # initial status
            is_active=True,
            user_detail=userdt,
            fees=fees,
            total_amount=int(amount)+int(fees),
        )
        # print(f'{service=}')

        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        success_data = service
        return confirmation_view(request,service=service)
        # Redirect or render confirmation page
        # return redirect('recharge_success')
    return render(request, 'recharge/mobile_prepaid.html', {'states': states,'user_data':user_data , 'success_data':success_data})

from django.forms.models import model_to_dict



def confirmation_view(request, service=None):
    if 'user_data' not in request.session:
        return redirect('sign_in')

    user_data = request.session.get('user_data', {})

    service_fields = {}
    if service:
        # Convert model to dictionary (only fields, no _state)
        service_fields = model_to_dict(service)

    return render(
        request,
        'recharge/confirmation_page.html',
        {
            'user_data': user_data,
            'service': service,
            'service_fields': service_fields
        }
    )

def recharge_success(request):
    last_id = request.session.get('last_service_id')
    if last_id:
        service = get_object_or_404(Service, pk=last_id)
        service.status = 'success'
        service.save()
    return render(request, "recharge/recharge_success.html")

# def recharge_success_view(request):
#     user_data = request.session.get('user_data', {})
#     service_id = request.session.get('last_service_id')
#     service = Service.objects.filter(id=service_id).first()
#     return render(request,'recharge/recharge_success.html', {'service': service,'user_data':user_data})



'''
===============================================================================================================
                            Mobile Postpaid method
===============================================================================================================
'''


def mobile_postpaid_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    
  
    success_data = None
    if request.method == 'POST':
        service_type = 'mobile_postpaid' #request.POST.get('service_type')
        refrence = request.POST.get('refrence')
        rechargers_number = request.POST.get('rechargers_number')
        
        
        # Save data to the database
        service = Service.objects.create(
            service_type=service_type,
            refrence = refrence,
            rechargers_number=rechargers_number,
            status='pending',   # initial status
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        success_data = service
        return confirmation_view(request,service=service)

    return render(request, 'recharge/mobile_postpaid.html', {'user_data': user_data,'success_data':success_data})



'''
===============================================================================================================
                            Recharge DTH method
===============================================================================================================
'''
def dth_recharge_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
        
    user_data = request.session.get('user_data', {})
    success_data = None
    if request.method == 'POST':
        service_type = 'dth' #request.POST.get('service_type')
        refrence = request.POST.get('refrence')
        rechargers_number = request.POST.get('rechargers_number')
        
        # Save data to the database
        service = Service.objects.create(
            service_type=service_type,
            refrence = refrence,
            rechargers_number=rechargers_number,
            status='failed',   # initial status
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        success_data = service
        return confirmation_view(request,service=service)
    return render(request, 'recharge/dth_recharge.html', {'user_data': user_data,'success_data':success_data})




'''
===============================================================================================================
                            Fastag Recharge method
===============================================================================================================
'''
# def fastag_recharge_view(request):
#     if 'user_data' not in request.session: 
#         return redirect('sign_in') 
#     user_data = request.session.get('user_data', {})
#     return render(request, 'recharge/fastag_recharge.html', {'user_data': user_data})

# def fastag_recharge_view(request):
#     if 'user_data' not in request.session: 
#         return redirect('sign_in') 
        
#     user_data = request.session.get('user_data', {})
#     success_data = None
#     if request.method == 'POST':
#         service_type = 'fastag' #request.POST.get('service_type')
#         refrence = request.POST.get('refrence')
#         rechargers_number = request.POST.get('rechargers_number')
        
#         # Save data to the database
#         service = Service.objects.create(
#             service_type=service_type,
#             refrence = refrence,
#             rechargers_number=rechargers_number,
#             status='failed',   # initial status
#             is_active=True,
#             user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
#         )
#         success_data = service
#         # Optional: store service id in session
#         request.session['last_service_id'] = service.id
#         success_data = service
#         return confirmation_view(request,service=service)
#     return render(request, 'recharge/fastag_recharge.html', {'user_data': user_data,'success_data':success_data})



'''
===============================================================================================================
                            Electricity method
===============================================================================================================
'''

def electricity_bill_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')
        amount = request.POST.get('amount')
        service_type = 'electricity_bill' #request.POST.get('service_type')
        refrence = request.POST.get('refrence')
        # print(f'{refrence=}')

        if selected_state_id:
            state = State.objects.get(id=selected_state_id)

            service = Service.objects.create(
                related_state=state,
                rechargers_number=rechargers_number,
                service_type=service_type,
                amount=amount if amount else None,
                refrence = refrence,
                status='failed',   # initial status
                is_active=True,
            
            
             user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
            )
            success_data = service
            # Optional: store service id in session
            request.session['last_service_id'] = service.id
            success_data = service
            return confirmation_view(request,service=service)
            # success_data = service
            # messages.success(request, f"{state.name} saved successfully!")

    return render(request, 'recharge/electricity_bill.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })


# '''
# ===============================================================================================================
#                             Rent method
# ===============================================================================================================
# '''

# def rental_view(request):
#     if 'user_data' not in request.session: 
#         return redirect('sign_in') 
#     user_data = request.session.get('user_data', {})
#     states = State.objects.all().order_by('name')
#     success_data = None

#     if request.method == 'POST':
#         selected_state_id = request.POST.get('related_state')
#         rechargers_number = request.POST.get('rechargers_number')
        
#         service_type = 'electricity_bill' #request.POST.get('service_type')
#         refrence = request.POST.get('refrence')
#         # print(f'{refrence=}')

#         if selected_state_id:
#             state = State.objects.get(id=selected_state_id)

#             service = Service.objects.create(
#                 related_state=state,
#                 rechargers_number=rechargers_number,
#                 service_type=service_type,
#                 refrence = refrence,
#                 status='failed',   # initial status
#                 is_active=True,
            
            
#              user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
#             )
#             success_data = service
#             # Optional: store service id in session
#             request.session['last_service_id'] = service.id
#             success_data = service
#             return confirmation_view(request,service=service)
#             # success_data = service
#             # messages.success(request, f"{state.name} saved successfully!")

#     return render(request, 'recharge/electricity_bill.html', {
#         'user_data': user_data,
#         'states': states,
#         'success_data': success_data
#     })


'''
===============================================================================================================
                            Recharge fees method
===============================================================================================================
'''

def education_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')
        
        service_type = 'education_fees' #request.POST.get('service_type')
        refrence = request.POST.get('refrence')
        # print(f'{refrence=}')

        if selected_state_id:
            state = State.objects.get(id=selected_state_id)

            service = Service.objects.create(
                related_state=state,
                rechargers_number=rechargers_number,
                service_type=service_type,
                refrence = refrence,
                status='failed',   # initial status
                is_active=True,
            
            
             user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
            )
            success_data = service
            # Optional: store service id in session
            request.session['last_service_id'] = service.id
            success_data = service
            return confirmation_view(request,service=service)
            # success_data = service
            # messages.success(request, f"{state.name} saved successfully!")

    return render(request, 'recharge/education_fees.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })

# def education_view(request):
#     if 'user_data' not in request.session: 
#         return redirect('sign_in') 
#     user_data = request.session.get('user_data', {})
#     states = State.objects.all().order_by('name')
#     return render(request,'recharge/education_fees.html',{'user_data':user_data,'states':states})

'''
===============================================================================================================
                            water bill method
===============================================================================================================
'''


def water_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')
        
        service_type = 'water_bill' #request.POST.get('service_type')
        refrence = request.POST.get('refrence')
        # print(f'{refrence=}')

        if selected_state_id:
            state = State.objects.get(id=selected_state_id)

            service = Service.objects.create(
                related_state=state,
                rechargers_number=rechargers_number,
                service_type=service_type,
                refrence = refrence,
                status='failed',   # initial status
                is_active=True,
            
            
             user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
            )
            success_data = service
            # Optional: store service id in session
            request.session['last_service_id'] = service.id
            success_data = service
            return confirmation_view(request,service=service)
            # success_data = service
            # messages.success(request, f"{state.name} saved successfully!")

    return render(request, 'recharge/water_bill.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })

# def water_view(request):
#     if 'user_data' not in request.session: 
#         return redirect('sign_in') 
#     user_data = request.session.get('user_data', {})
#     states = State.objects.all().order_by('name')
#     # print(f'{states=}')
#     states = State.objects.all().order_by('name')
#     return render(request,'recharge/water_bill.html',{'user_data':user_data,'states':states})



'''
===============================================================================================================
                            lpg_book_gas method
===============================================================================================================
'''
def lpg_book_gas_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')
        
        service_type = 'lpg_gas_bill' #request.POST.get('service_type')
        refrence = request.POST.get('refrence')
        selected_state_id = request.POST.get('related_state')

        # print(f'{refrence=}')

        if selected_state_id:
            state = State.objects.get(id=selected_state_id)

            service = Service.objects.create(
                related_state=state,
                rechargers_number=rechargers_number,
                service_type=service_type,
                refrence = refrence,
                status='failed',   # initial status
                is_active=True,
            
            
             user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
            )
            success_data = service
            # Optional: store service id in session
            request.session['last_service_id'] = service.id
            success_data = service
            return confirmation_view(request,service=service)
            # success_data = service
            # messages.success(request, f"{state.name} saved successfully!")

    return render(request, 'recharge/lpg_book_gas.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })


# def lpg_book_gas_view(request):
#     if 'user_data' not in request.session: 
#         return redirect('sign_in') 
#     user_data = request.session.get('user_data', {})
#     states = State.objects.all().order_by('name')
#     # print(f'{states=}')
#     states = State.objects.all().order_by('name')
#     return render(request,'recharge/lpg_book_gas.html',{'user_data':user_data,'states':states})



'''
===============================================================================================================
                            lpg_book_gas method
===============================================================================================================
'''

def rental_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')
        # amount = request.POST.get('amount')
        
        service_type = 'rent_bill'
        refrence = request.POST.get('refrence')

        # print(f'{refrence=}')

        if selected_state_id:
            state = State.objects.get(id=selected_state_id)

            service = Service.objects.create(
                related_state=state,
                rechargers_number=rechargers_number,
                service_type=service_type,
                # amount=amount if amount else None,
                refrence = refrence,
                status='failed',   # initial status
                is_active=True,
            
            
             user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
            )
            success_data = service
            # Optional: store service id in session
            request.session['last_service_id'] = service.id
            success_data = service
            return confirmation_view(request,service=service)
            # success_data = service
            # messages.success(request, f"{state.name} saved successfully!")

    return render(request, 'recharge/rental.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })




'''
===============================================================================================================
                            landline postpaid method
===============================================================================================================
'''

def landline_postpaid_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    success_data = None

    if request.method == 'POST':
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'landline_postpaid'
        refrence = request.POST.get('refrence')

        service = Service.objects.create(
            rechargers_number=rechargers_number,
            service_type=service_type,
            refrence=refrence,
            status='pending',   # initial status
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        return confirmation_view(request, service=service)

    return render(request, 'recharge/landline_postpaid.html', {
        'user_data': user_data,
        'success_data': success_data
    })



'''
===============================================================================================================
                            cable_tv_view method
===============================================================================================================
'''

def cable_tv_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    success_data = None

    if request.method == 'POST':
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'cable_tv'
        refrence = request.POST.get('refrence')

        service = Service.objects.create(
            rechargers_number=rechargers_number,
            service_type=service_type,
            refrence=refrence,
            status='pending',   # initial status
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        return confirmation_view(request, service=service)

    return render(request, 'recharge/cable_tv.html', {
        'user_data': user_data,
        'success_data': success_data
    })



'''
===============================================================================================================
                            genric_gas_view method
===============================================================================================================
'''

def generic_gas_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    success_data = None

    if request.method == 'POST':
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'generic_gas'
        refrence = request.POST.get('refrence')

        service = Service.objects.create(
            rechargers_number=rechargers_number,
            service_type=service_type,
            refrence=refrence,
            status='pending',   # initial status
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        return confirmation_view(request, service=service)

    return render(request, 'recharge/generic_gas.html', {
        'user_data': user_data,
        'success_data': success_data
    })


'''
===============================================================================================================
                            genric_gas_view method
===============================================================================================================
'''

def brosdband_postpaid_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    success_data = None

    if request.method == 'POST':
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'broadband_postpaid'
        refrence = request.POST.get('refrence')

        service = Service.objects.create(
            rechargers_number=rechargers_number,
            service_type=service_type,
            refrence=refrence,
            status='pending',   # initial status
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        return confirmation_view(request, service=service)

    return render(request, 'recharge/brosdband_postpaid.html', {
        'user_data': user_data,
        'success_data': success_data
    })




'''
===============================================================================================================
                            Insurance method
===============================================================================================================
'''

def insurance_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    success_data = None

    if request.method == 'POST':
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'insurance'
        refrence = request.POST.get('refrence')

        service = Service.objects.create(
            rechargers_number=rechargers_number,
            service_type=service_type,
            refrence=refrence,
            status='pending',   # initial status
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        return confirmation_view(request, service=service)

    return render(request, 'recharge/insurance.html', {
        'user_data': user_data,
        'success_data': success_data
    })

'''
===============================================================================================================
                            Municiple Taxes method
===============================================================================================================
'''

def municiple_taxes_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'municipal_taxes'
        refrence = request.POST.get('refrence')

        if selected_state_id:
            state = State.objects.get(id=selected_state_id)

            service = Service.objects.create(
                related_state=state,
                rechargers_number=rechargers_number,
                service_type=service_type,
                refrence=refrence,
                status='pending',   # initial status
                is_active=True,
                user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
            )
            success_data = service
            # Optional: store service id in session
            request.session['last_service_id'] = service.id
            return confirmation_view(request, service=service)

    return render(request, 'recharge/municiple_taxes.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })


'''
===============================================================================================================
                            Subscription method
===============================================================================================================
'''

def subscription_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    success_data = None

    if request.method == 'POST':
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'subscription'
        refrence = request.POST.get('refrence')

        service = Service.objects.create(
            rechargers_number=rechargers_number,
            service_type=service_type,
            refrence=refrence,
            status='pending',   # initial status
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        return confirmation_view(request, service=service)

    return render(request, 'recharge/subscription.html', {
        'user_data': user_data,
        'success_data': success_data
    })


'''
===============================================================================================================
                           Club & Association method
===============================================================================================================
'''

def club_assiciation_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'club_association'
        refrence = request.POST.get('refrence')

        if selected_state_id:
            state = State.objects.get(id=selected_state_id)

            service = Service.objects.create(
                related_state=state,
                rechargers_number=rechargers_number,
                service_type=service_type,
                refrence=refrence,
                status='pending',   # initial status
                is_active=True,
                user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
            )
            success_data = service
            # Optional: store service id in session
            request.session['last_service_id'] = service.id
            return confirmation_view(request, service=service)

    return render(request, 'recharge/club_association.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })




'''
===============================================================================================================
                           Club & Association method
===============================================================================================================
'''

def donation_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'donation'
        refrence = request.POST.get('refrence')

        if selected_state_id:
            state = State.objects.get(id=selected_state_id)

            service = Service.objects.create(
                related_state=state,
                rechargers_number=rechargers_number,
                service_type=service_type,
                refrence=refrence,
                status='pending',   # initial status
                is_active=True,
                user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
            )
            success_data = service
            # Optional: store service id in session
            request.session['last_service_id'] = service.id
            return confirmation_view(request, service=service)

    return render(request, 'recharge/donation.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })





'''
===============================================================================================================
                          EV Recharge method
===============================================================================================================
'''

def ev_recharge_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'ev_recharge'
        refrence = request.POST.get('refrence')
        amount = request.POST.get('amount')

        if selected_state_id:
            state = State.objects.get(id=selected_state_id)

            service = Service.objects.create(
                related_state=state,
                rechargers_number=rechargers_number,
                service_type=service_type,
                refrence=refrence,
                amount=amount if amount else None,
                status='pending',   # initial status
                is_active=True,
                user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
            )
            success_data = service
            # Optional: store service id in session
            request.session['last_service_id'] = service.id
            return confirmation_view(request, service=service)

    return render(request, 'recharge/ev_recharge.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })




'''
===============================================================================================================
                          Housing Society method
===============================================================================================================
'''

def housing_society_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'housing_society'
        refrence = request.POST.get('refrence')
        amount = request.POST.get('amount')

        if selected_state_id:
            state = State.objects.get(id=selected_state_id)

            service = Service.objects.create(
                related_state=state,
                rechargers_number=rechargers_number,
                service_type=service_type,
                refrence=refrence,
                amount=amount if amount else None,
                status='pending',   # initial status
                is_active=True,
                user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
            )
            success_data = service
            # Optional: store service id in session
            request.session['last_service_id'] = service.id
            return confirmation_view(request, service=service)

    return render(request, 'recharge/housing_society.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })



'''
===============================================================================================================
                          Municiple Services method
===============================================================================================================
'''

def municiple_services_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'municiple_services'
        refrence = request.POST.get('refrence')
        amount = request.POST.get('amount')

        if selected_state_id:
            state = State.objects.get(id=selected_state_id)

            service = Service.objects.create(
                related_state=state,
                rechargers_number=rechargers_number,
                service_type=service_type,
                refrence=refrence,
                amount=amount if amount else None,
                status='pending',   # initial status
                is_active=True,
                user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
            )
            success_data = service
            # Optional: store service id in session
            request.session['last_service_id'] = service.id
            return confirmation_view(request, service=service)

    return render(request, 'recharge/municiple_services.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })



'''
===============================================================================================================
                          Recurring deposite method
===============================================================================================================
'''

def recurring_deposite_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'recurring_deposit'
        refrence = request.POST.get('refrence')
        amount = request.POST.get('amount')

        state = None
        if selected_state_id:
            state = State.objects.get(id=selected_state_id)

        service = Service.objects.create(
            related_state=state,
            rechargers_number=rechargers_number,
            service_type=service_type,
            refrence=refrence,
            amount=amount if amount else None,
            status='pending',   # initial status
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        return confirmation_view(request, service=service)

    return render(request, 'recharge/recurring_deposite.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })
'''
===============================================================================================================
                          Credit Card method
===============================================================================================================
'''

def credit_card_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'credit_card'
        refrence = request.POST.get('refrence')
        amount = request.POST.get('amount')

        related_state = None
        if selected_state_id:
            related_state = State.objects.filter(id=selected_state_id).first()

        service = Service.objects.create(
            related_state=related_state,
            rechargers_number=rechargers_number,
            service_type=service_type,
            refrence=refrence,
            amount=amount if amount else None,
            status='pending',   # initial status
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        return confirmation_view(request, service=service)

    return render(request, 'recharge/credit_card.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })
    





'''
===============================================================================================================
                         E challan method
===============================================================================================================
'''

def e_challan_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')  # Vehicle Number
        service_type = 'e_challan'  # ye e challan ka h
        refrence = request.POST.get('refrence')  # Challan Number
        amount = request.POST.get('amount')

        related_state = None
        if selected_state_id:
            related_state = State.objects.filter(id=selected_state_id).first()

        service = Service.objects.create(
            related_state=related_state,
            rechargers_number=rechargers_number,
            service_type=service_type,
            refrence=refrence,
            amount=amount if amount else None,
            status='pending',   # initial status
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        return confirmation_view(request, service=service)

    return render(request, 'recharge/e_challan.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })


'''
===============================================================================================================
                         E challan method
===============================================================================================================
'''

def loan_repayment_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')  # Loan Account Number
        service_type = 'loan_repayment'  # ye loan repayment ka h
        refrence = request.POST.get('refrence')  # Bank/Lender Name
        loan_type = request.POST.get('loan_type', '')  # Loan Type (optional)
        amount = request.POST.get('amount')

        # Combine loan type with reference if provided
        if loan_type:
            refrence = f"{refrence} - {loan_type}" if refrence else loan_type

        related_state = None
        if selected_state_id:
            related_state = State.objects.filter(id=selected_state_id).first()

        service = Service.objects.create(
            related_state=related_state,
            rechargers_number=rechargers_number,
            service_type=service_type,
            refrence=refrence,
            amount=amount if amount else None,
            status='pending',   # initial status
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        return confirmation_view(request, service=service)

    return render(request, 'recharge/loan_repayment.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })

'''
===============================================================================================================
                        National Pension System method
===============================================================================================================
'''

def national_pension_system_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')  # PRAN (Permanent Retirement Account Number)
        service_type = 'national_pension_system'
        pop_sp = request.POST.get('pop_sp', '')  # POP-SP (Point of Presence - Service Provider)
        tier_type = request.POST.get('tier_type', '')  # Tier Type (Tier I or Tier II)
        amount = request.POST.get('amount')

        # Combine tier type with POP-SP reference
        refrence = pop_sp
        if tier_type:
            refrence = f"{pop_sp} - {tier_type}" if pop_sp else tier_type

        related_state = None
        if selected_state_id:
            related_state = State.objects.filter(id=selected_state_id).first()

        service = Service.objects.create(
            related_state=related_state,
            rechargers_number=rechargers_number,
            service_type=service_type,
            refrence=refrence,
            amount=amount if amount else None,
            status='pending',   # initial status
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        return confirmation_view(request, service=service)

    return render(request, 'recharge/national_pension_system.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })




'''
===============================================================================================================
                        Prepaid meter method
===============================================================================================================
'''

def prepaid_meter_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')  # Consumer/Connection Number
        service_type = 'prepaid_meter'  # Prepaid meter service type
        refrence = request.POST.get('refrence')  # Electricity Board/Utility Provider
        amount = request.POST.get('amount')

        related_state = None
        if selected_state_id:
            related_state = State.objects.filter(id=selected_state_id).first()

        service = Service.objects.create(
            related_state=related_state,
            rechargers_number=rechargers_number,
            service_type=service_type,
            refrence=refrence,
            amount=amount if amount else None,
            status='pending',   # initial status
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        return confirmation_view(request, service=service)

    return render(request, 'recharge/prepaid_meter.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })




'''
===============================================================================================================
                      NCMC Recharge method
===============================================================================================================
'''
def ncmc_recharge_view(request):
    if 'user_data' not in request.session:
        return redirect('sign_in')

    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        card_number = request.POST.get('card_number')  # NCMC Card Number
        issuer = request.POST.get('issuer')            # Card Issuer/Bank
        amount = request.POST.get('amount')            # Recharge Amount

        related_state = None
        if selected_state_id:
            related_state = State.objects.filter(id=selected_state_id).first()

        # Service model according to ncmc recharge form structure
        service = Service.objects.create(
            related_state=related_state,
            rechargers_number=card_number,       # Card Number stored here
            service_type='ncmc_recharge',        # Consistent snake_case for internal service type
            refrence=issuer,                     # Card issuer saved as reference
            amount=amount if amount else None,
            status='pending',
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        request.session['last_service_id'] = service.id
        return confirmation_view(request, service=service)

    return render(request, 'recharge/ncmc_recharge.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })




'''
===============================================================================================================
                      Fleet Card Recharge method
===============================================================================================================
'''

def fleet_card_recharge_view(request):
    if 'user_data' not in request.session:
        return redirect('sign_in')

    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        card_number = request.POST.get('card_number')  # Fleet Card Number
        issuer = request.POST.get('issuer')            # Card Issuer/Bank
        amount = request.POST.get('amount')            # Recharge Amount

        related_state = None
        if selected_state_id:
            related_state = State.objects.filter(id=selected_state_id).first()

        # Service model according to fleet card recharge form structure
        service = Service.objects.create(
            related_state=related_state,
            rechargers_number=card_number,       # Fleet Card Number stored here
            service_type='fleet_card_recharge',  # Use the correct service type for fleet card recharge
            refrence=issuer,                     # Card issuer saved as reference
            amount=amount if amount else None,
            status='pending',
            is_active=True,
            user_detail=f'{user_data.get("username")}-({user_data.get("userid")})',
        )
        success_data = service
        request.session['last_service_id'] = service.id
        return confirmation_view(request, service=service)

    return render(request, 'recharge/fleet_card_recharge.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })


'''
===============================================================================================================
                    Agent Collection method
===============================================================================================================
'''

def agent_collection_view(request):

    if 'user_data' not in request.session:
        return redirect('sign_in')

    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        agent_id = request.POST.get('agent_id')               # Agent ID or billing reference number
        bill_number = request.POST.get('bill_number')         # Bill Number
        agency_name = request.POST.get('agency_name')         # Name of Collection Agency/Agent
        amount = request.POST.get('amount') 
                        
        related_state = None
        if selected_state_id:
            related_state = State.objects.filter(id=selected_state_id).first()

        # Store agency_name in the 'user_detail' or other available fields, as 'Service' model does not have extra_data
        user_detail = f'{user_data.get("username")}-({user_data.get("userid")}) | Agency: {agency_name}'

        service = Service.objects.create(
            related_state=related_state,
            rechargers_number=agent_id,              # Storing Agent ID (or any unique identifier)
            service_type='agent_collection',         # Use correct service type present in Service.SERVICE_CHOICES
            refrence=bill_number,                    # Bill number as reference
            amount=amount if amount else None,
            status='pending',
            is_active=True,
            user_detail=user_detail
        )
        success_data = service
        print(f'{success_data=}')
        # print(f'{success_data=}')
        request.session['last_service_id'] = service.id
        return confirmation_view(request, service=service)

    return render(request, 'recharge/agent_collection.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })


    
'''
===============================================================================================================
                            Transaction History method
===============================================================================================================
'''


# def transaction_history_view(request):
#     if 'user_data' not in request.session: 
#         return redirect('sign_in') 
#     user_data = request.session.get('user_data', {})

#     # Base queryset (show only recent records)
#     services = Service.objects.all().order_by('-id')
#     # print(f'{services=}')

#     # --- Filtering logic ---
#     month = request.GET.get('month')
#     category = request.GET.get('category')
#     status = request.GET.get('status')
#     search = request.GET.get('search')

#     if month:
#         services = services.filter(created_at__month=month)
#     if category:
#         services = services.filter(service_type=category)
#     if status:
#         services = services.filter(status=status.lower())
#     if search:
#         services = services.filter(rechargers_number__icontains=search) | services.filter(refrence__icontains=search)

#     return render(request, 'recharge/transaction_history.html', {
#         'user_data': user_data,
#         'services': services,
#     })

from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Service
from datetime import datetime
from django.utils import timezone

def transaction_history_view(request):
    if 'user_data' not in request.session:
        return redirect('sign_in')
    user_data = request.session.get('user_data', {})

    # services = Service.objects.all().order_by('-id')
    user_data = request.session.get('user_data', {})
    userid = user_data.get('userid')
    username = user_data.get('username')
    userdt = f'{username}-({userid})'

   # services = Service.objects.all().order_by('-id')
    services = Service.objects.filter(user_detail = userdt ).order_by('-id')
    # Get filters
    start_date_str = request.GET.get('start_date', '').strip()
    end_date_str = request.GET.get('end_date', '').strip()
    category = request.GET.get('category', '').strip()
    status = request.GET.get('status', '').strip()
    search = request.GET.get('search', '').strip()

    # Parse and apply date range filter (expects YYYY-MM-DD)
    start_date = None
    end_date = None
    date_error = None

    # Helper to parse date string
    def parse_date(dstr):
        try:
            # parse as date
            return datetime.strptime(dstr, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return None

    if start_date_str:
        start_date = parse_date(start_date_str)
        if start_date is None:
            date_error = "Invalid start date format. Use YYYY-MM-DD."

    if end_date_str:
        end_date = parse_date(end_date_str)
        if end_date is None:
            date_error = "Invalid end date format. Use YYYY-MM-DD."

    # If both present and valid, ensure start <= end
    if start_date and end_date and start_date > end_date:
        # swap or set error — here we swap so UI remains flexible
        start_date, end_date = end_date, start_date

    # Apply date filters
    if start_date:
        services = services.filter(create_date__date__gte=start_date)
    if end_date:
        services = services.filter(create_date__date__lte=end_date)

    # Category filter (validate against choices)
    if category:
        allowed_categories = [choice[0] for choice in Service.SERVICE_CHOICES]
        if category in allowed_categories:
            services = services.filter(service_type=category)

    # Status filter
    if status:
        allowed_status = [s[0] for s in Service.STATUS_CHOICES]
        if status in allowed_status:
            services = services.filter(status=status)

    # Search across number, reference, orderid
    if search:
        services = services.filter(
            Q(rechargers_number__icontains=search) |
            Q(refrence__icontains=search) |
            Q(orderid__icontains=search)
        )

    # Prepare select options
    categories = [('', 'Category')] + list(Service.SERVICE_CHOICES)
    statuses = [('', 'Status')] + list(Service.STATUS_CHOICES)

    context = {
        'user_data': user_data,
        'services': services,
        'categories': categories,
        'statuses': statuses,
        'selected_category': category,
        'selected_status': status,
        'search_query': search,
        'start_date': start_date_str,
        'end_date': end_date_str,
        'date_error': date_error,
    }
    return render(request, 'recharge/transaction_history.html', context)

   
from django.http import HttpResponse



'''
===============================================================================================================
                            Not found method
===============================================================================================================
'''

def not_found_page(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    return render(request,'recharge/not_foung_page.html',{'user_data':user_data})


'''
===============================================================================================================
                            Complain history method
===============================================================================================================
'''

def complain_history_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    return render(request,'recharge/complain_history.html',{'user_data':user_data})




'''
===============================================================================================================
                         Privacy policy method
===============================================================================================================
'''
def privacy_policy_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    return render(request,'recharge/privacy_policy.html',{'user_data':user_data})



def term_of_us_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    return render(request,'recharge/term_of_us.html',{'user_data':user_data})


def refund_policy_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    return render(request,'recharge/refund_policy.html',{'user_data':user_data})


def about_us_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    return render(request,'recharge/about_us.html',{'user_data':user_data})


def cookie_policy_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    return render(request,'recharge/cookie_policy.html',{'user_data':user_data})


def team_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    return render(request,'recharge/team.html',{'user_data':user_data})


def career_page_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    return render(request,'recharge/career.html',{'user_data':user_data})


def bbps_tsp_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    return render(request,'recharge/bbps_tsp.html',{'user_data':user_data})

def receipt_view(request, id):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    service = get_object_or_404(Service, pk=id)
   
    # print(f'{service=}')
    return render(request,'recharge/receipt.html',{'user_data':user_data, 'service':service})

def query_transaction(request):
    user_data = request.session.get('user_data', {})

    return render(request,'recharge/query_transaction.html',{'user_data':user_data})
def raise_complain_view(request):
    user_data = request.session.get('user_data', {})

    return render(request,'recharge/raise_complaint_page.html',{'user_data':user_data})



def check_complaint_status(request):
    user_data = request.session.get('user_data', {})

    return render(request,'recharge/check_complain_status.html',{'user_data':user_data})


def sms_slip_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    return render(request,'recharge/sms_slip.html',{'user_data':user_data})