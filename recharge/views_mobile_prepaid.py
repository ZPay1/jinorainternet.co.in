from urllib import request
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render
# from .models import Service
from django.shortcuts import render, redirect
from django.contrib import messages
from lelifeproject.views import refresh_tokents
import requests
Baseurl = "https://api.jinora.co.in/api"
import requests
from django.shortcuts import render, redirect

import json
import requests

   
'''
===============================================================================================================
                       Category method
===============================================================================================================
'''

def mobile_prepaid_category_view(request):
    if 'access_token' not in request.session:
        return redirect('sign_in') 

    access_token = request.session.get("access_token")
    user_data = request.session.get("user_data", {})
 
    category = request.GET.get("category", "Mobile Prepaid")

    billers = []

    def mobile_prepaid_category_data(token):
        return requests.get(
            f"{Baseurl}/npci/get-biller-by-category/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            params={"category": category},
            timeout=10
        )

    response = mobile_prepaid_category_data(access_token)
    # print(f'{response=}')
    # 🔁 Token expire case
    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get('access_token')
            response = mobile_prepaid_category_data(new_token)
        else:
            messages.error(request, "Session expired. Please login again.")
            return redirect('sign_in')

    # ✅ Success response
    try:
        if response.status_code == 200:
            data = response.json()
            # print(f'{data=}')
            if data.get("status"):
                billers = data.get("data", [])
    except Exception as e:
        messages.error(request, f"API request failed: {str(e)}")
        return redirect('sign_in')

    return render(request, "recharge_mo_prepaid/mobile_prepaid_billers.html", {
        "billers": billers,
        "category": category,
        "user_data": user_data,
        'access_token':access_token
    })


'''
===============================================================================================================
                       Plans method
===============================================================================================================
'''


def mobile_prepaid_plans_view(request):
    if 'access_token' not in request.session:
        return redirect('sign_in') 
    access_token = request.session.get("access_token")
    user_data = request.session.get("user_data", {})

    # access_token = request.session["user_data"]["access"]
    biller_id = request.GET.get("billerId")

    planDetails = []
    params={"billerId": biller_id}
    print(f'{params=}')
    def fetch_plans(token):
    
        return requests.get(
            f"{Baseurl}/npci/mobile-prepaid/fetch-plans-by-biller/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            params=params,
            timeout=10
        )
    

    response = fetch_plans(access_token)
    print(f'{response=}')
    # 🔁 TOKEN EXPIRED CASE (same as category view)
    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get("access_token")
            response = fetch_plans(new_token)
        else:
            messages.error(request, "Session expired. Please login again.")
            return redirect("sign_in")

    # ✅ SUCCESS RESPONSE
    try:
        if response.status_code == 200:
            data = response.json()
            print(f'{data=}')

            if (
                response.status_code == 200
                and data.get("status") is True
                and data.get("data", {}).get("status") == "SUCCESS"
            ):
                planDetails = data["data"]["payload"]["planDetails"]
                print(f'{planDetails=}')
           
            # if data.get("status"):
            #     plans = data.get("data", {})
            #     # print(f'rrrr{plans=}')
            #     if plans.get("status") == "SUCCESS":
            #         payload = plans.get("payload", {})
            #         planDetails = payload.get("planDetails", [])
                    # print(f'{planDetails=}')
            else:
                messages.error(request, data.get("message", "No plans found"))
    except Exception as e:
        messages.error(request, f"API request failed: {str(e)}")
        return redirect("sign_in")

    return render(request, "recharge_mo_prepaid/mobile_prepaid_plans.html", {
        "plans": planDetails,
        "billerId": biller_id,
        "user_data": user_data,
        'access_token':access_token
    })



'''
===============================================================================================================
                       Validate method
===============================================================================================================
'''

def mobile_prepaid_validate_view(request):

    if 'access_token' not in request.session:
        return redirect('sign_in')

    access_token = request.session.get("access_token")
    user_data = request.session.get("user_data", {})

    def fetch_plans(token, biller_id):
        return requests.get(
            f"{Baseurl}/npci/mobile-prepaid/fetch-plans-by-biller/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            params={"billerId": biller_id},
            timeout=10
        )

    def validate_plan(token, payload):
        return requests.post(
            f"{Baseurl}/npci/mobile-prepaid/validate/",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=15
        )

    if request.method == "POST":
        mobile_number = request.POST.get("mobile_number")
        circle = request.POST.get("circle")
        plan_id = request.POST.get("plan_id")
        biller_id = request.POST.get("billerId")

        # 🔁 STEP 1: Fetch plans
        response = fetch_plans(access_token, biller_id)

        # 🔁 TOKEN EXPIRED CASE
        if response.status_code in (401, 403):
            if refresh_tokents(request):
                access_token = request.session.get("access_token")
                response = fetch_plans(access_token, biller_id)
            else:
                messages.error(request, "Session expired. Please login again.")
                return redirect("sign_in")

        if response.status_code != 200:
            messages.error(request, "Unable to fetch plans")
            return redirect("mobile_prepaid_plans")

        data = response.json()
        # print(f'{data=}')
        plan_list = (
            data.get("data", {})
                .get("payload", {})
                .get("planDetails", [])
        )

        # 🔍 STEP 2: Find selected plan
        selected_plan = next(
            (p for p in plan_list if str(p.get("id")) == str(plan_id)),
            None
        )

        if not selected_plan:
            messages.error(request, "Invalid plan selected")
            return redirect("mobile_prepaid_plans")

        # 🔁 STEP 3: Validate plan
        validate_payload = {
            "mobile_number": mobile_number,
            "circle": circle,
            "plan": selected_plan
        }

        validate_response = validate_plan(access_token, validate_payload)
        # print(f'{validate_response=}')
        # 🔁 TOKEN EXPIRED CASE (validate API)
        if validate_response.status_code in (401, 403):
            if refresh_tokents(request):
                access_token = request.session.get("access_token")
                validate_response = validate_plan(access_token, validate_payload)
            else:
                messages.error(request, "Session expired. Please login again.")
                return redirect("sign_in")

        validate_data = validate_response.json()
        # print(f'{validate_data=}')
        if validate_response.status_code == 200 and validate_data.get("status"):
            # 🔐 STORE IN SESSION
            request.session["MOBILE_PREPAID_CONFIRM"] = {
                "mobile_number": mobile_number,
                "circle": circle,
                "plan": selected_plan,
                "amount": validate_data.get("amount"),
                "return_payload": validate_data.get("return_payload"),
            }
            return redirect("mobile_prepaid_confirm")

        messages.error(request, validate_data.get("message", "Validation failed"))
        return redirect('mobile_prepaid_category')

    return render(
        request,
        "recharge_mo_prepaid/mobile_prepaid_fetch.html",
        {
            "user_data": user_data,
            "access_token": access_token
        }
    )




'''
===============================================================================================================
                       Confirm method
===============================================================================================================
'''
def mobile_prepaid_confirm(request):
    # access_token = request.session.get("access_token")
    user_data = request.session.get("user_data", {})

    if 'access_token' not in request.session:
        return redirect('sign_in') 
        

        
    data = request.session["MOBILE_PREPAID_CONFIRM"]
    context = {
        "mobile_number": data.get("mobile_number"),
        "circle": data.get("circle"),
        "plan": data.get("plan"),
        "amount": data.get("amount"),
        "txn": data.get("return_payload"),
        "user_data": user_data,
    }

    return render(
        request,
        "recharge_mo_prepaid/mobile_prepaid_confirm.html",
        context
    )


'''
===============================================================================================================
                       Payment method
===============================================================================================================
'''
from datetime import datetime
def mobile_prepaid_payment(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    # biller_type = request.GET.get("biller_type", "Mobile Prepaid")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")
    if "MOBILE_PREPAID_CONFIRM" not in request.session:
            return redirect("mobile_prepaid_category")

    bill = request.session.get("MOBILE_PREPAID_CONFIRM", {})

    def make_payment(token, payload):
        return requests.post(
            f"{Baseurl}/recharge-payment/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
            timeout=20
        )

    # Initialize these as None to avoid UnboundLocalError
    data = None
    receipt = None

    if request.method == "POST":
        amount = request.POST.get("amount")
        tpin = request.POST.get("tpin")

        payload = {
            "amount": amount,
            "tpin": tpin,
            "biller_type": 'Mobile Prepaid',
            "return_payload": bill.get("return_payload", {})
        }
        # print(f'{payload=}')

        try:
            # 🔹 First attempt
            response = make_payment(access_token, payload)
            # print(f'{response=}')
            # 🔁 Token expired → refresh & retry
            if response.status_code in (401, 403):
                if refresh_tokents(request):
                    new_token = request.session.get("access_token")
                    response = make_payment(new_token, payload)
                else:
                    messages.error(request, "Session expired. Please login again.")
                    return redirect("sign_in")

            data = response.json()
            print(f'{data=}')
            # ✅ SUCCESS
            if (
                response.status_code == 200
                and data.get("status") is True
                and data.get("bill_data", {}).get("status") == "SUCCESS"
            ):
                success_payload = data["bill_data"]["payload"]
            # ✅ Time formatting
                raw_time = success_payload.get("timeStamp")
                formatted_time = ""

                if raw_time:
                    # timezone part remove karo
                    clean_time = raw_time.split("+")[0]
                    formatted_time = datetime.strptime(
                        clean_time, "%Y-%m-%dT%H:%M:%S"
                    ).strftime("%d %b %Y, %I:%M %p")
                # ❌ Prevent double payment
                request.session.pop("MOBILE_PREPAID_CONFIRM", None)

                receipt = {
                    "customer_name": data.get("name", ""),
                    "amount": amount,
                    "refid": success_payload.get("refId", ""),

                    "time": formatted_time,

                    "transaction_id": success_payload.get("additionalParams", {}).get("transactionID", ""),
                    "reference_id": success_payload.get("additionalParams", {}).get("txnReferenceId", ""),
                    "biller_reference_number": success_payload.get("additionalParams", {}).get("billerReferenceNumber", ""),
                    "approval_ref": success_payload.get("reason", {}).get("approvalRefNum", ""),
                    "responseCode": success_payload.get("reason", {}).get("responseCode", ""),
                    "responseReason": success_payload.get("reason", {}).get("responseReason", ""),
            
                    "mobile": data.get("mobile", ""),
                    "self_cashback": data.get("self_cashback", ""),
                    "biller_type": "Mobile Prepaid",
                }

                return render(
                    request,
                    "recharge_mo_prepaid/mobile_prepaid_success.html",
                    {
                        "message": data.get("message"),
                        "receipt": receipt,
                        "user_data": user_data,
                    }
                )

            # ❌ FAILED
            error_message = (
                data.get("error", {})
                .get("payload", {})
                .get("errors", [{}])[0]
                .get("reason")
                or data.get("message", "Payment Failed")
            )

            messages.error(request, error_message)
            return redirect("mobile_prepaid_confirm")

        except requests.RequestException:
            messages.error(request, "Network error. Please try again.")
            return redirect("mobile_prepaid_confirm")

        except Exception:
         
            messages.error(request, "Server error. Please try again.")
            return redirect("mobile_prepaid_confirm")
    return render(request, "recharge_mo_prepaid/mobile_prepaid_success.html",
                  {
                      "message": data.get("message") if data else "",
                      "receipt": receipt if receipt else {},
                      "user_data": user_data,
                  }
                )


