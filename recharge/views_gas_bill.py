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

'''
===============================================================================================================
                        Category method
===============================================================================================================
'''
def gas_category_view(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    category = request.GET.get("category", "Gas")
    billers = []

    def gas_category_data(token):
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
    response = gas_category_data(access_token)
    # print(f'{response=}')
    # 🔁 Step 2: Token expired → refresh → retry
    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get("access_token")
            response = gas_category_data(new_token)
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
            messages.error(request, "Unable to fetch billers from gas server.")

    except Exception:
        messages.error(request, "Invalid response from gas server.")

    return render(request, "gas_bill/gas_billers.html", {
        "billers": billers,
        "category": category,
        "user_data": user_data
    })


'''
===============================================================================================================
                        Fetch bIll method
===============================================================================================================
'''


def gas_fetch_bill(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if request.method == "POST":
        Consumer_number = request.POST.get("Consumer_number")
        distributor_id = request.POST.get("distributor_id")
        billerId = request.POST.get("billerId")


        # print(f'{Consumer_number,distributor_id=}')
        # print(f'{billerId=}')

        if not Consumer_number or not distributor_id:
            messages.error(request, "Please enter Consumer number or distribution id.")
            return redirect("gas_fetch")

        def gas_fetch_bill_data(token):
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return requests.post(
                f"{Baseurl}/npci/fetch-gas-bill/",
                json={
                    "Consumer_Number": Consumer_number,
                    "Distributor_ID": distributor_id,
                    "billerId": billerId
                },
                headers=headers,
                timeout=15
            )


        # 🔁 Step 1: First API call
        response = gas_fetch_bill_data(access_token)
        # print(f'{response=}')
        # 🔁 Step 2: Token expired → refresh → retry
        if response.status_code in (401, 403):
            if refresh_tokents(request):
                new_token = request.session.get("access_token")
                response = gas_fetch_bill_data(new_token)
            else:
                messages.error(request, "Session expired. Please login again.")
                return redirect("sign_in")

        try:
            data = response.json()
            # print(f"{data=}")
            if response.status_code == 200 and data.get("status"):
                # 🔐 Store bill data in session
                print({
                    "Consumer_number": Consumer_number,
                    "distributor_id": distributor_id,
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                })
                request.session["GAS_BILL"] = {
                    "Consumer_number": Consumer_number,
                    'distributor_id':distributor_id,
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                }
                return redirect("gas_bill_confirm")

            else:
                messages.error(request, "Unable to fetch gas bill")

        except Exception:
            messages.error(request, "Invalid response from gas server.")

    return render(request, "gas_bill/gas_fetch.html", {
        "user_data": user_data
    })


'''
===============================================================================================================
                        Confirm method
===============================================================================================================
'''

def gas_bill_confirm(request):
    # 🔐 Session safety
    if "GAS_BILL" not in request.session:
        # return redirect("gas_fetch")
        return redirect("gas_category")

    bill = request.session.get("GAS_BILL", {})
    # print(f'{bill=}')
    user_data = request.session.get("user_data", {})

    payload = bill.get("payload", {})
    # print(f'{payload=}')
  

    context = {
        "Consumer_number": bill.get("Consumer_number"),
        "distributor_id": bill.get("distributor_id"),
        "billerId": bill.get("billerId"),

        "payload": payload,
        # "biller": biller_response,
        # "additional": additional,
        "user_data": user_data,
    }

    return render(request, "gas_bill/gas_confirm.html", context)





'''
===============================================================================================================
                       Payment method
===============================================================================================================
'''
def gas_bill_payment(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    bill = request.session.get("GAS_BILL", {})
    # print(f'{bill=}')
    def gas_payment_api(token, payload):
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
            "biller_type": "Gas",
            "return_payload": bill.get("return_payload", {})
        }

        try:
            # 🔁 First payment attempt
            res = gas_payment_api(access_token, payload)
            # print(f'{res=}')
            # 🔁 TOKEN EXPIRED CASE
            if res.status_code in (401, 403):
                if refresh_tokents(request):
                    access_token = request.session.get("access_token")
                    res = gas_payment_api(access_token, payload)
                else:
                    messages.error(request, "Session expired. Please login again.")
                    return redirect("sign_in")

            data = res.json()
            # print(f'{data=}')
            # ✅ SUCCESS
            if (
                res.status_code == 200
                and data.get("status") is True
                and data.get("bill_data", {}).get("status") == "SUCCESS"
            ):
                success_payload = data["bill_data"]["payload"]

                # ✅ prevent double payment
                request.session.pop("GAS_BILL", None)

                receipt = {
                    "customer_name": data.get("name", ""),
                    "amount": amount,
                    "Consumer_number": bill.get("return_payload", {}).get("customerParams", {}).get("CUstomer ID Registration Number", ""),
                    "distributor_id": bill.get("return_payload", {}).get("customerParams", {}).get("Distributor id Registration ID", ""),

                    "transaction_id": success_payload.get("additionalParams", {}).get("transactionID", ""),
                    "reference_id": success_payload.get("additionalParams", {}).get("txnReferenceId", ""),
                    "distributor_contact": success_payload.get("additionalParams", {}).get("Distributor Contact", ""),
                    "distributor_name": success_payload.get("additionalParams", {}).get("Distributor Name", ""),
                    "consumer_number": success_payload.get("additionalParams", {}).get("Consumer Number", ""),
                    "consumer_address": success_payload.get("additionalParams", {}).get("Consumer Address", ""),

                    "Outstanding_Amount": success_payload.get("additionalParams", {}).get("Total Outstanding Amount", ""),
                    "approval_ref": success_payload.get("reason", {}).get("approvalRefNum", ""),
                    "responseReason":success_payload.get("reason", {}).get("responseReason", ""),
                    "time": success_payload.get("timeStamp", ""),
                    "status": data.get("data", {}).get("status"),
                    # "status":bill.get("return_payload", {}).get("status", {}),
                    "mobile": data.get("mobile", ""),
                    "self_cashback": data.get("self_cashback", ""),
                    "biller_type": "Gas",
                }

                return render(request, "gas_bill/gas_success.html", {
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
            return redirect("gas_bill_confirm")

        except requests.RequestException:
            messages.error(request, "Server error. Please try again.")
            return redirect("gas_bill_confirm")

    return redirect("gas_bill_confirm")
