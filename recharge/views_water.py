from urllib import request
from django.shortcuts import render, redirect
from django.contrib import messages
from lelifeproject.views import refresh_tokents
import requests

from django.conf import settings
Baseurl = f"{settings.JINORA_API_BASE}"

'''
===============================================================================================================
                        Category method
===============================================================================================================
'''
def water_category_view(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    # For water, set category as "Water"
    category = request.GET.get("category", "Water")
    billers = []

    def water_category_data(token):
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
    response = water_category_data(access_token)
    # 🔁 Step 2: Token expired → refresh → retry
    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get("access_token")
            response = water_category_data(new_token)
        else:
            messages.error(request, "Session expired. Please login again.")
            return redirect("sign_in")

    try:
        # ✅ Parse response safely
        data = response.json()
        if response.status_code == 200 and data.get("status"):
            billers = data.get("data", [])
        else:
            messages.error(request, "Unable to fetch billers from Water server.")

    except Exception:
        messages.error(request, "Invalid response from Water server.")

    return render(request, "water/water_billers.html", {
        "billers": billers,
        "category": category,
        "user_data": user_data
    })

'''
===============================================================================================================
                        Fetch bIll method
===============================================================================================================
'''

def water_fetch_bill(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if request.method == "POST":
        Form_No = request.POST.get("Form_No")
        billerId = request.POST.get("billerId")

        print(f'{Form_No=}')
        print(f'{billerId=}')

        if not Form_No :
            messages.error(request, "Please enter Consumer Number or DOB.")
            return redirect("water_fetch")

        def water_fetch_bill_data(token):
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return requests.post(
                f"{Baseurl}/npci/fetch-water-bill/",
                json={
                    "Form_No": Form_No,
                    "billerId": billerId
                },
                headers=headers,
                timeout=15
            )

        # 🔁 Step 1: First API call
        response = water_fetch_bill_data(access_token)
        print(f'{response=}')
        # 🔁 Step 2: Token expired → refresh → retry
        if response.status_code in (401, 403):
            if refresh_tokents(request):
                new_token = request.session.get("access_token")
                response = water_fetch_bill_data(new_token)
            else:
                messages.error(request, "Session expired. Please login again.")
                return redirect("sign_in")

        try:
            data = response.json()
            print(f"{data=}")
            if response.status_code == 200 and data.get("status"):
                # 🔐 Store bill data in session
                print({
                    "Form_No": Form_No,
                    
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                })
                request.session["WATER_BILL"] = {
                    "Form_No": Form_No,
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                }
                return redirect("water_confirm")

            else:
                messages.error(request, "Unable to fetch Water bill")
                return redirect('water_category')

        except Exception:
            messages.error(request, "Invalid response from Water server.")

    return render(request, "water/water_fetch.html", {
        "user_data": user_data
    })

'''
===============================================================================================================
                        Confirm method
===============================================================================================================
'''

def water_bill_confirm(request):
    # 🔐 Session safety
    if "WATER_BILL" not in request.session:
        return redirect("water_category")

    bill = request.session.get("WATER_BILL", {})
    user_data = request.session.get("user_data", {})

    payload = bill.get("payload", {})

    context = {
        "Form_No": bill.get("Form_No"),
        "billerId": bill.get("billerId"),
        "payload": payload,
        "user_data": user_data,
    }

    return render(request, "water/water_confirm.html", context)

'''
===============================================================================================================
                       Payment method
===============================================================================================================
'''

from datetime import datetime
def water_payment(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    bill = request.session.get("WATER_BILL", {})
    def water_payment_api(token, payload):
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
        amount = request.POST.get("amount")
        tpin = request.POST.get("tpin")

        payload = {
            "amount": amount,
            "tpin": tpin,
            "biller_type": "Water",
            "return_payload": bill.get("return_payload", {})
        }

        try:
            res = water_payment_api(access_token, payload)
            print(f'{res=}')
            if res.status_code in (401, 403):
                if refresh_tokents(request):
                    access_token = request.session.get("access_token")
                    res = water_payment_api(access_token, payload)
                else:
                    messages.error(request, "Session expired. Please login again.")
                    return redirect("sign_in")

            data = res.json()
            print(f'{data=}')
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
                    # timezone part remove karo
                    clean_time = raw_time.split("+")[0]
                    formatted_time = datetime.strptime(
                        clean_time, "%Y-%m-%dT%H:%M:%S"
                    ).strftime("%d %b %Y, %I:%M %p")
                # ✅ prevent double payment
                request.session.pop("WATER_BILL", None)

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
                    "responseReason": success_payload.get("reason", {}).get("responseReason", ""),
                    
                    "status": data.get("data", {}).get("status"),
                    "mobile": data.get("mobile", ""),
                    "self_cashback": data.get("self_cashback", ""),
                    "biller_type": "Water",
                }

                return render(request, "water/water_success.html", {
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

            messages.error(request, error_message)
            return redirect("water_confirm")

        except requests.RequestException:
            messages.error(request, "Server error. Please try again.")
            return redirect("water_confirm")

    return redirect("water_confirm")
