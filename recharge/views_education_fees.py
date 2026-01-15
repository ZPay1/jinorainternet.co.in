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
def education_fees_category_view(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    category = request.GET.get("category", "Education Fees")
    billers = []

    def education_fees_category_data(token):
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
    response = education_fees_category_data(access_token)
    # #print(f'{response=}')
    # 🔁 Step 2: Token expired → refresh → retry
    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get("access_token")
            response = education_fees_category_data(new_token)
        else:
            messages.error(request, "Session expired. Please login again.")
            return redirect("sign_in")

    try:
        # ✅ Parse response safely
        data = response.json()
        # #print(f"{data=}")

        if response.status_code == 200 and data.get("status"):
            billers = data.get("data", [])
            # #print(f'{billers=}')
        else:
            messages.error(request, "Unable to fetch billers from Education Fees server.")

    except Exception:
        messages.error(request, "Invalid response from Education Fees server.")
        return redirect('education_category')
    return render(request, "education_Fees/edu_fees_billers.html", {
        "billers": billers,
        "category": category,
        "user_data": user_data
    })


'''
===============================================================================================================
                        Fetch bIll method
===============================================================================================================
'''


def education_fees_fetch_bill(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if request.method == "POST":
        Roll_No = request.POST.get("Roll_No")
        billerId = request.POST.get("billerId")


        #print(f'{Roll_No,=}')
        #print(f'{billerId=}')

        if not Roll_No :
            messages.error(request, "Please enter Roll Number.")
            return redirect("education_fetch")

        def education_fees_fetch_bill_data(token):
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return requests.post(
                f"{Baseurl}/npci/fetch-education-fees-bill/",
                json={
                    "Roll_No": Roll_No,
                    "billerId": billerId
                },
                headers=headers,
                timeout=15
            )


        # 🔁 Step 1: First API call
        response = education_fees_fetch_bill_data(access_token)
        #print(f'{response=}')
        # 🔁 Step 2: Token expired → refresh → retry
        if response.status_code in (401, 403):
            if refresh_tokents(request):
                new_token = request.session.get("access_token")
                response = education_fees_fetch_bill_data(new_token)
            else:
                messages.error(request, "Session expired. Please login again.")
                return redirect("sign_in")

        try:
            data = response.json()
            #print(f"{data=}")
            if response.status_code == 200 and data.get("status"):
                # 🔐 Store bill data in session
                #print({
                #     "Roll_No": Roll_No,
                #     "billerId": billerId,
                #     "payload": data.get("data", {}).get("payload"),
                #     "return_payload": data.get("return_payload"),
                # })
                request.session["EDUCATION_FEES_BILL"] = {
                    "Roll_No": Roll_No,
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                }
                return redirect("education_confirm")

            else:
                messages.error(request, "Unable to fetch Education Fees  bill")
                return redirect('education_fetch')
        except Exception:
            messages.error(request, "Invalid response from Education Fees  server.")

    return render(request, "education_Fees/edu_fees_fetch.html", {
        "user_data": user_data
    })


'''
===============================================================================================================
                        Confirm method
===============================================================================================================
'''

def education_fees_bill_confirm(request):
    # 🔐 Session safety
    if "EDUCATION_FEES_BILL" not in request.session:
        # return redirect("education_fetch")
        return redirect("education_category")

    bill = request.session.get("EDUCATION_FEES_BILL", {})
    # #print(f'{bill=}')
    user_data = request.session.get("user_data", {})

    payload = bill.get("payload", {})
    # #print(f'{payload=}')
  

    context = {
        "Roll_No": bill.get("Roll_No"),
        "billerId": bill.get("billerId"),

        "payload": payload,
        "user_data": user_data,
    }

    return render(request, "education_Fees/edu_fees_confirm.html", context)





'''
===============================================================================================================
                       Payment method
===============================================================================================================
'''

from datetime import datetime
def education_fees_payment(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    bill = request.session.get("EDUCATION_FEES_BILL", {})
    # #print(f'{bill=}')
    def education_fees_payment_api(token, payload):
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
            "biller_type": "Education Fees",
            "return_payload": bill.get("return_payload", {})
        }

        try:
            # 🔁 First payment attempt
            res = education_fees_payment_api(access_token, payload)
            #print(f'{res=}')
            # 🔁 TOKEN EXPIRED CASE
            if res.status_code in (401, 403):
                if refresh_tokents(request):
                    access_token = request.session.get("access_token")
                    res = education_fees_payment_api(access_token, payload)
                else:
                    messages.error(request, "Session expired. Please login again.")
                    return redirect("sign_in")

            data = res.json()
            #print(f'{data=}')
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
                request.session.pop("EDUCATION_FEES_BILL", None)

                receipt = {
                    "customer_name": data.get("name", ""),
                    "amount": amount,
                    "refid": success_payload.get("refId", ""),
                    
                    "time": formatted_time,
                    "transaction_id": success_payload.get("additionalParams", {}).get("transactionID", ""),
                    "reference_id": success_payload.get("additionalParams", {}).get("txnReferenceId", ""),
                   "biller_reference_number": success_payload.get("additionalParams", {}).get("billerReferenceNumber", ""),
                    "biller_unique_number": success_payload.get("additionalParams", {}).get("Biller Unique Number", ""),
                    # "Outstanding_Amount": success_payload.get("additionalParams", {}).get("Total Outstanding Amount", ""),
                    "approval_ref": success_payload.get("reason", {}).get("approvalRefNum", ""),
                    "responseCode": success_payload.get("reason", {}).get("responseCode", ""),
                    "responseReason":success_payload.get("reason", {}).get("responseReason", ""),
                    # "time": success_payload.get("timeStamp", ""),
                    "status": data.get("data", {}).get("status"),
                    # "status":bill.get("return_payload", {}).get("status", {}),
                    "mobile": data.get("mobile", ""),
                    "self_cashback": data.get("self_cashback", ""),
                    "biller_type": "Education Fees",
                }

                return render(request, "education_Fees/edu_fees_success.html", {
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
            # #print(f'{error_message=}')

            messages.error(request, error_message)
            return redirect("education_confirm")

        except requests.RequestException:
            messages.error(request, "Server error. Please try again.")
            return redirect("education_confirm")

    return redirect("education_confirm")
