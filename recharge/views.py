from django.shortcuts import render
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

# def mobile_prepaid_view(request):
#     user_data = request.session.get('user_data', {})

#     return render(request,'recharge/mobile_prepaid.html',{'user_data':user_data})

from django.shortcuts import render, redirect
from .models import Service, State

'''
===============================================================================================================
                            Mobile Prepaid method
===============================================================================================================
'''

def mobile_prepaid_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    # print(f'{states=}')
    success_data = None
    if request.method == 'POST':
        rechargers_number = request.POST.get('rechargers_number')
        service_type = 'mobile_prepaid' #request.POST.get('service_type')
        state_id = request.POST.get('related_state')
        refrence = request.POST.get('refrence')
        amount = request.POST.get('amount')
        related_state = State.objects.filter(id=state_id).first()
        

        # Save data to the database
        service = Service.objects.create(
            service_type=service_type,
            rechargers_number=rechargers_number,
            related_state=related_state,
            amount=amount,
            refrence = refrence,
            status='failed',   # initial status
            is_active=True
        )
        print(f'{service=}')

        # Optional: store service id in session
        request.session['last_service_id'] = service.id
        success_data = service
        # Redirect or render confirmation page
        # return redirect('recharge_success')
    return render(request, 'recharge/mobile_prepaid.html', {'states': states,'user_data':user_data , 'success_data':success_data})




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
        return redirect('login') 
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
            status='failed',   # initial status
            is_active=True
        )
        success_data = service

    return render(request, 'recharge/mobile_postpaid.html', {'user_data': user_data,'success_data':success_data})



'''
===============================================================================================================
                            Recharge DTH method
===============================================================================================================
'''
def dth_recharge_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
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
            is_active=True
        )
        success_data = service
    return render(request, 'recharge/dth_recharge.html', {'user_data': user_data,'success_data':success_data})




'''
===============================================================================================================
                            Fastag Recharge method
===============================================================================================================
'''
def fastag_recharge_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})
    return render(request, 'recharge/fastag_recharge.html', {'user_data': user_data})





'''
===============================================================================================================
                            Electricity method
===============================================================================================================
'''

def electricity_bill_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    success_data = None

    if request.method == 'POST':
        selected_state_id = request.POST.get('related_state')
        rechargers_number = request.POST.get('rechargers_number')
        
        service_type = 'electricity_bill' #request.POST.get('service_type')
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
                is_active=True
            
            )
            success_data = service
            messages.success(request, f"{state.name} saved successfully!")

    return render(request, 'recharge/electricity_bill.html', {
        'user_data': user_data,
        'states': states,
        'success_data': success_data
    })



'''
===============================================================================================================
                            Recharge fees method
===============================================================================================================
'''
def education_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    return render(request,'recharge/education_fees.html',{'user_data':user_data,'states':states})

'''
===============================================================================================================
                            water bill method
===============================================================================================================
'''
def water_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    # print(f'{states=}')
    states = State.objects.all().order_by('name')
    return render(request,'recharge/water_bill.html',{'user_data':user_data,'states':states})



'''
===============================================================================================================
                            lpg_book_gas method
===============================================================================================================
'''
def lpg_book_gas_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})
    states = State.objects.all().order_by('name')
    # print(f'{states=}')
    states = State.objects.all().order_by('name')
    return render(request,'recharge/lpg_book_gas.html',{'user_data':user_data,'states':states})


'''
===============================================================================================================
                            Transaction History method
===============================================================================================================
'''


def transaction_history_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})

    # Base queryset (show only recent records)
    services = Service.objects.all().order_by('-id')

    # --- Filtering logic ---
    month = request.GET.get('month')
    category = request.GET.get('category')
    status = request.GET.get('status')
    search = request.GET.get('search')

    if month:
        services = services.filter(created_at__month=month)
    if category:
        services = services.filter(service_type=category)
    if status:
        services = services.filter(status=status.lower())
    if search:
        services = services.filter(rechargers_number__icontains=search) | services.filter(refrence__icontains=search)

    return render(request, 'recharge/transaction_history.html', {
        'user_data': user_data,
        'services': services,
    })

   
from django.http import HttpResponse

'''
===============================================================================================================
                            Recharge method
===============================================================================================================
'''


def recharge_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})
    return render(request,'recharge/recharge_page.html',{'user_data':user_data})

'''
===============================================================================================================
                            Not found method
===============================================================================================================
'''

def not_found_page(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})
    return render(request,'recharge/not_foung_page.html',{'user_data':user_data})


'''
===============================================================================================================
                            Complain history method
===============================================================================================================
'''

def complain_history_view(request):
    if 'user_data' not in request.session: 
        return redirect('login') 
    user_data = request.session.get('user_data', {})
    return render(request,'recharge/complain_history.html',{'user_data':user_data})









