from urllib import request
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render
# from .models import Service
from django.shortcuts import render, redirect
from django.contrib import messages
from lelifeproject.views import refresh_tokents
import requests
from django.conf import settings
Baseurl = f"{settings.JINORA_API_BASE}"
import requests
from django.shortcuts import render, redirect

'''
===============================================================================================================
                        Category method
===============================================================================================================
'''
def insurance_category_view(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    category = request.GET.get("category", "Insurance")
    billers = []

    def insurance_category_data(token):
        return requests.get(
            f"{Baseurl}/npci/get-biller-by-category/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            params={"category": category},
            timeout=10
        )

    # 🔁 Step 1: First API call
    response = insurance_category_data(access_token)
    # print(f'{response=}')
    # 🔁 Step 2: Token expired → refresh → retry
    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get("access_token")
            response = insurance_category_data(new_token)
        else:
            messages.error(request, "Session expired. Please login again.")
            return redirect("sign_in")

    try:
        # ✅ Parse response safely
        data = response.json()
        # print(f"{data=}")

        if response.status_code == 200 and data.get("status"):
            billers = data.get("data", [])
            # print(f'{billers=}')
        else:
            messages.error(request, "Unable to fetch billers from Insurance server.")

    except Exception:
        messages.error(request, "Invalid response from Insurance server.")
        return redirect('insurance_category')
    return render(request, "Insurance/insurance_billers.html", {
        "billers": billers,
        "category": category,
        "user_data": user_data
    })


'''
===============================================================================================================
                        Fetch bIll method
===============================================================================================================
'''


def insurance_fetch_bill(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if request.method == "POST":
        Policy_Number = request.POST.get("Policy_Number")
        dob = request.POST.get("dob")
        billerId = request.POST.get("billerId")


        print(f'{Policy_Number,dob=}')
        print(f'{billerId=}')

        if not Policy_Number or not dob :
            messages.error(request, "Please enter Policy Number or DOB. ")
            return redirect("insurance_fetch")

        def insurance_fetch_bill_data(token):
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return requests.post(
                f"{Baseurl}/npci/fetch-insurance-bill/",
                json={
                    "Policy_Number": Policy_Number,
                    'dob':dob,
                    "billerId": billerId
                },
                headers=headers,
                timeout=15
            )


        # 🔁 Step 1: First API call
        response = insurance_fetch_bill_data(access_token)
        print(f'{response=}')
        # 🔁 Step 2: Token expired → refresh → retry
        if response.status_code in (401, 403):
            if refresh_tokents(request):
                new_token = request.session.get("access_token")
                response = insurance_fetch_bill_data(new_token)
            else:
                messages.error(request, "Session expired. Please login again.")
                return redirect("sign_in")

        try:
            data = response.json()
            print(f"{data=}")
            if response.status_code == 200 and data.get("status"):
                # 🔐 Store bill data in session
                print({
                    "Policy_Number": Policy_Number,
                    'dob':dob,
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                })
                request.session["INSURANEC_BILL"] = {
                    "Policy_Number": Policy_Number,
                    'dob':dob,
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                }
                return redirect("insurance_confirm")

            else:
                messages.error(request, "Unable to fetch Insurance  bill")
               

        except Exception:
            messages.error(request, "Invalid response from Insurance  server.")

    return render(request, "Insurance/insurance_fetch.html", {
        "user_data": user_data
    })


'''
===============================================================================================================
                        Confirm method
===============================================================================================================
'''

def insurance_bill_confirm(request):
    # 🔐 Session safety
    if "INSURANEC_BILL" not in request.session:
        # return redirect("insurance_fetch")
        return redirect("insurance_category")

    bill = request.session.get("INSURANEC_BILL", {})
    # print(f'{bill=}')
    user_data = request.session.get("user_data", {})

    payload = bill.get("payload", {})
    # print(f'{payload=}')
  

    context = {      
        "Policy_Number": bill.get("Policy_Number"),
        "dob": bill.get("dob"),
        "billerId": bill.get("billerId"),

        "payload": payload,
        # "biller": biller_response,
        # "additional": additional,
        "user_data": user_data,
    }

    return render(request, "Insurance/insurance_confirm.html", context)





'''
===============================================================================================================
                       Payment method
===============================================================================================================
'''
from datetime import datetime

def insurance_payment(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if "INSURANEC_BILL" not in request.session:
        return redirect("insurance_category")

    bill = request.session.get("INSURANEC_BILL", {})
    # print(f'{bill=}')
    def insurance_payment_api(token, payload):
        return requests.post(
            f"{Baseurl}/recharge-payment/",
            json=payload,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=20
        )

    if request.method == "POST":
        # # ✅ IMPORTANT: amount session se lo (validated amount)
        # amount = bill.get("payload", {}).get("billAmount") or bill.get("amount")
        amount = request.POST.get("amount")
        tpin = request.POST.get("tpin")

        payload = {
            "amount": amount,
            "tpin": tpin,
            "biller_type": "Insurance",
            "return_payload": bill.get("return_payload", {})
        }

        try:
            # 🔁 First payment attempt
            res = insurance_payment_api(access_token, payload)
            print(f'{res=}')
            # 🔁 TOKEN EXPIRED CASE
            if res.status_code in (401, 403):
                if refresh_tokents(request):
                    access_token = request.session.get("access_token")
                    res = insurance_payment_api(access_token, payload)
                else:
                    messages.error(request, "Session expired. Please login again.")
                    return redirect("sign_in")

            data = res.json()
            print(f'{data=}')
            # ✅ SUCCESS
            if (
                res.status_code == 200
                and data.get("status") is True
                and data.get("bill_data", {}).get("status") == "SUCCESS"
            ):
                success_payload = data["bill_data"]["payload"]
                # ✅ Time formatting
                raw_time = success_payload.get("timeStamp")
                formatted_time = ""

                if raw_time:
                    # Remove timezone
                    clean_time = raw_time.split("+")[0]
                    formatted_time = datetime.strptime(
                        clean_time, "%Y-%m-%dT%H:%M:%S"
                    ).strftime("%d %b %Y, %I:%M %p")

                request.session.pop("HEALTH_INSURANCE_BILL", None)

                # ✅ prevent double payment
                request.session.pop("INSURANEC_BILL", None)

                receipt = {
                    "customer_name": data.get("name", ""),
                    "amount": amount,
                    "refid": success_payload.get("refId", ""),

                    "time": formatted_time,

                    "transaction_id": success_payload.get("additionalParams", {}).get("transactionID", ""),
                    "reference_id": success_payload.get("additionalParams", {}).get("txnReferenceId", ""),
                   "biller_reference_number": success_payload.get("additionalParams", {}).get("billerReferenceNumber", ""),
                    # "biller_unique_number": success_payload.get("additionalParams", {}).get("Biller Unique Number", ""),
                    # "Outstanding_Amount": success_payload.get("additionalParams", {}).get("Total Outstanding Amount", ""),
                    "approval_ref": success_payload.get("reason", {}).get("approvalRefNum", ""),
                    "responseCode": success_payload.get("reason", {}).get("responseCode", ""),
                    "responseReason":success_payload.get("reason", {}).get("responseReason", ""),
                    # "time": success_payload.get("timeStamp", ""),
                    "status": data.get("data", {}).get("status"),
                    # "status":bill.get("return_payload", {}).get("status", {}),
                    "mobile": data.get("mobile", ""),
                    "self_cashback": data.get("self_cashback", ""),
                    "biller_type": "Insurance",
                }

                return render(request, "Insurance/insurance_success.html", {
                    "message": data.get("message"),
                    "receipt": receipt,
                    "user_data": user_data
                })

            # ❌ FAILED PAYMENT
            error_message = (
                data.get("error", {})
                    .get("payload", {})
                    .get("errors", [{}])[0]
                    .get("errorDtl")
                or data.get("message", "Payment Failed")
            )
            # print(f'{error_message=}')

            messages.error(request, error_message)
            return redirect("insurance_confirm")

        except requests.RequestException:
            messages.error(request, "Server error. Please try again.")
            return redirect("insurance_confirm")

    return redirect("insurance_confirm")
