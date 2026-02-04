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
def loan_category_view(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    category = request.GET.get("category", "Loan Repayment")
    billers = []

    def loan_category_data(token):
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
    response = loan_category_data(access_token)
    # print(f'{response=}')
    # 🔁 Step 2: Token expired → refresh → retry
    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get("access_token")
            response = loan_category_data(new_token)
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
            messages.error(request, "Unable to fetch billers from Loan Repayment server.")

    except Exception:
        messages.error(request, "Invalid response from Loan Repayment server.")

    return render(request, "loan_repayment_bill/loan_billers.html", {
        "billers": billers,
        "category": category,
        "user_data": user_data
    })


'''
===============================================================================================================
                        Fetch bIll method
===============================================================================================================
'''


def loan_fetch_bill(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if request.method == "POST":
        Loan_Number = request.POST.get("Loan_Number")
        billerId = request.POST.get("billerId")


        print(f'{Loan_Number,=}')
        print(f'{billerId=}')

        if not Loan_Number :
            messages.error(request, "Please enter Loan Number.")
            return redirect("loan_fetch")

        def loan_fetch_bill_data(token):
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return requests.post(
                f"{Baseurl}/npci/fetch-loan-repayment-bill/",
                json={
                    "Loan_Number": Loan_Number,
                    "billerId": billerId
                },
                headers=headers,
                timeout=15
            )


        # 🔁 Step 1: First API call
        response = loan_fetch_bill_data(access_token)
        print(f'{response=}')
        # 🔁 Step 2: Token expired → refresh → retry
        if response.status_code in (401, 403):
            if refresh_tokents(request):
                new_token = request.session.get("access_token")
                response = loan_fetch_bill_data(new_token)
            else:
                messages.error(request, "Session expired. Please login again.")
                return redirect("sign_in")

        try:
            data = response.json()
            print(f"{data=}")
            if response.status_code == 200 and data.get("status"):
                # 🔐 Store bill data in session
                print({
                    "Loan_Number": Loan_Number,
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                })
                request.session["LOAN_REPAYMENT_BILL"] = {
                    "Loan_Number": Loan_Number,
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                }
                return redirect("loan_confirm")

            else:
                messages.error(request, "Unable to fetch Loan Repayment bill")

        except Exception:
            messages.error(request, "Invalid response from Loan Repayment server.")
            return redirect('loan_category')
    return render(request, "loan_repayment_bill/loan_fetch.html", {
        "user_data": user_data
    })


'''
===============================================================================================================
                        Confirm method
===============================================================================================================
'''

def loan_bill_confirm(request):
    # 🔐 Session safety
    if "LOAN_REPAYMENT_BILL" not in request.session:
        # return redirect("loan_fetch")
        return redirect("loan_category")

    bill = request.session.get("LOAN_REPAYMENT_BILL", {})
    print(f'{bill=}')
    user_data = request.session.get("user_data", {})

    payload = bill.get("payload", {})
    # print(f'{payload=}')
  

    context = {
        "Loan_Number": bill.get("Loan_Number"),
        "billerId": bill.get("billerId"),

        "payload": payload,
        # "biller": biller_response,
        # "additional": additional,
        "user_data": user_data,
    }

    return render(request, "loan_repayment_bill/loan_confirm.html", context)





'''
===============================================================================================================
                       Payment method
===============================================================================================================
'''
from datetime import datetime
def loan_bill_payment(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    bill = request.session.get("LOAN_REPAYMENT_BILL", {})
    # print(f'{bill=}')
    def loan_payment_api(token, payload):
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
            "biller_type": "Loan Repayment",
            "return_payload": bill.get("return_payload", {})
        }

        try:
            # 🔁 First payment attempt
            res = loan_payment_api(access_token, payload)
            print(f'{res=}')
            # 🔁 TOKEN EXPIRED CASE
            if res.status_code in (401, 403):
                if refresh_tokents(request):
                    access_token = request.session.get("access_token")
                    res = loan_payment_api(access_token, payload)
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
                    # timezone part remove karo
                    clean_time = raw_time.split("+")[0]
                    formatted_time = datetime.strptime(
                        clean_time, "%Y-%m-%dT%H:%M:%S"
                    ).strftime("%d %b %Y, %I:%M %p")
                # ✅ prevent double payment
                request.session.pop("LOAN_REPAYMENT_BILL", None)

                receipt = {
                    "customer_name": data.get("name", ""),
                    "amount": amount,
                    
                    # "loan_number": bill.get("return_payload", {}).get("customerParams", {}).get("Loan Number Registration ID", ""),

                    "refid": success_payload.get("refId", ""),
                    
                    "time": formatted_time,
                    "transaction_id": success_payload.get("additionalParams", {}).get("transactionID", ""),
                    "reference_id": success_payload.get("additionalParams", {}).get("txnReferenceId", ""),
                   
                    "Outstanding_Amount": success_payload.get("additionalParams", {}).get("Total Outstanding Amount", ""),
                    "approval_ref": success_payload.get("reason", {}).get("approvalRefNum", ""),
                    "responseCode": success_payload.get("reason", {}).get("responseCode", ""),
                    "responseReason":success_payload.get("reason", {}).get("responseReason", ""),
                    # "time": success_payload.get("timeStamp", ""),
                    "status": data.get("data", {}).get("status"),
                    # "status":bill.get("return_payload", {}).get("status", {}),
                    "mobile": data.get("mobile", ""),
                    "self_cashback": data.get("self_cashback", ""),
                    "biller_type": "Loan Repayment",
                }

                return render(request, "loan_repayment_bill/loan_success.html", {
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
            return redirect("loan_confirm")

        except requests.RequestException:
            messages.error(request, "Server error. Please try again.")
            return redirect("loan_confirm")

    return redirect("loan_confirm")
