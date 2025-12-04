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
        print(f'{service=}')

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
def fastag_recharge_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    return render(request, 'recharge/fastag_recharge.html', {'user_data': user_data})





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
    return render(request,'recharge/education_fees.html',{'user_data':user_data,'states':states})

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
        return redirect('sign_in') 
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
                            Recharge method
===============================================================================================================
'''


def recharge_view(request):
    if 'user_data' not in request.session: 
        return redirect('sign_in') 
    user_data = request.session.get('user_data', {})
    return render(request,'recharge/recharge_page.html',{'user_data':user_data})

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
   
    print(f'{service=}')
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