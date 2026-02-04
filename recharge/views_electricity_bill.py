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
def electricity_category_view(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    category = request.GET.get("category", "Electricity")
    billers = []

    def electricity_category_data(token):
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
    response = electricity_category_data(access_token)
    # print(f'{response=}')
    # 🔁 Step 2: Token expired → refresh → retry
    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get("access_token")
            response = electricity_category_data(new_token)
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
            messages.error(request, "Unable to fetch billers from electricity server.")

    except Exception:
        messages.error(request, "Invalid response from electricity server.")
        return redirect('electricity_category')
    return render(request, "electricity_bill/electricity_billers.html", {
        "billers": billers,
        "category": category,
        "user_data": user_data
    })


'''
===============================================================================================================
                        Fetch bIll method
===============================================================================================================
'''


def electricity_fetch_bill(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if request.method == "POST":
        Consumer_Id = request.POST.get("Consumer_Id")
        billerId = request.POST.get("billerId")

        # print(f'{Consumer_Id=}')
        # print(f'{billerId=}')

        if not Consumer_Id or not billerId:
            messages.error(request, "Please enter Consumer ID.")
            return redirect("electricity_fetch")

        def electricity_fetch_bill_data(token):
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return requests.post(
                f"{Baseurl}/npci/fetch-electricity-bill/",
                json={
                    "Consumer_Id": Consumer_Id,
                    "billerId": billerId
                },
                headers=headers,
                timeout=15
            )

        # 🔁 Step 1: First API call
        response = electricity_fetch_bill_data(access_token)
        # print(f'{response=}')
        # 🔁 Step 2: Token expired → refresh → retry
        if response.status_code in (401, 403):
            if refresh_tokents(request):
                new_token = request.session.get("access_token")
                response = electricity_fetch_bill_data(new_token)
            else:
                messages.error(request, "Session expired. Please login again.")
                return redirect("sign_in")

        try:
            data = response.json()
            # print(f"{data=}")
            if response.status_code == 200 and data.get("status"):
                # 🔐 Store bill data in session
                # print({
                #     "Consumer_Id": Consumer_Id,
                #     "billerId": billerId,
                #     "payload": data.get("data", {}).get("payload"),
                #     "return_payload": data.get("return_payload"),
                # })
                request.session["ELECTRICITY_BILL"] = {
                    "Consumer_Id": Consumer_Id,
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                }
                return redirect("electricity_confirm")

            else:
                messages.error(request, "Unable to fetch electricity bill")

        except Exception:
            messages.error(request, "Invalid response from electricity server.")

    return render(request, "electricity_bill/electricity_fetch.html", {
        "user_data": user_data
    })


'''
===============================================================================================================
                        Confirm method
===============================================================================================================
'''

def electricity_confirm(request):
    # 🔐 Session safety
    if "ELECTRICITY_BILL" not in request.session:
        # return redirect("electricity_fetch")
        return redirect("electricity_category")

    bill = request.session.get("ELECTRICITY_BILL", {})
    # print(f'{bill=}')
    user_data = request.session.get("user_data", {})

    payload = bill.get("payload", {})
    # print(f'{payload=}')
 

    context = {
        "Consumer_Id": bill.get("Consumer_Id"),
        "billerId": bill.get("billerId"),

        "payload": payload,
        # "biller": biller_response,
        # "additional": additional,
        "user_data": user_data,
    }

    return render(request, "electricity_bill/electricity_confirm.html", context)





'''
===============================================================================================================
                       Payment method
===============================================================================================================
'''

from datetime import datetime
def electricity_payment(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")


    if "ELECTRICITY_BILL" not in request.session:
            # return redirect("electricity_fetch")
            return redirect("electricity_category")
    bill = request.session.get("ELECTRICITY_BILL", {})

    def electricity_payment_api(token, payload):
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
            "biller_type": "Electricity",
            "return_payload": bill.get("return_payload", {})
        }

        try:
            # 🔁 First payment attempt
            res = electricity_payment_api(access_token, payload)

            # 🔁 TOKEN EXPIRED CASE
            if res.status_code in (401, 403):
                if refresh_tokents(request):
                    access_token = request.session.get("access_token")
                    res = electricity_payment_api(access_token, payload)
                else:
                    messages.error(request, "Session expired. Please login again.")
                    return redirect("sign_in")

            data = res.json()

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

                # ✅ prevent double payment
                request.session.pop("ELECTRICITY_BILL", None)

                receipt = {
                    "customer_name": data.get("name", ""),
                    "amount": amount,
                    # "Consumer_Id": bill.get("return_payload", {}).get("customerParams", {}).get("CUstomer ID Registration Number", ""),
                    "refid": success_payload.get("refId", ""),
                    
                    "time": formatted_time,
                    "transaction_id": success_payload.get("additionalParams", {}).get("transactionID", ""),
                    "reference_id": success_payload.get("additionalParams", {}).get("txnReferenceId", ""),
                    "billerReferenceNumber": success_payload.get("additionalParams", {}).get("billerReferenceNumber", ""),
                    "biller_nique_number": success_payload.get("additionalParams", {}).get("Biller Unique Number", ""),
                    
                    "Outstanding_Amount": success_payload.get("additionalParams", {}).get("Total Outstanding Amount", ""),
                    "approval_ref": success_payload.get("reason", {}).get("approvalRefNum", ""),
                    "responseReason":success_payload.get("reason", {}).get("responseReason", ""),
                    # "time": success_payload.get("timeStamp", ""),
                    "status": data.get("data", {}).get("status"),
                    # "status":bill.get("return_payload", {}).get("status", {}),
                    "mobile": data.get("mobile", ""),
                    "self_cashback": data.get("self_cashback", ""),
                    "biller_type": "Electricity",
                }

                return render(request, "electricity_bill/electricity_success.html", {
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
            return redirect("electricity_confirm")

        except requests.RequestException:
            messages.error(request, "Server error. Please try again.")
            return redirect("electricity_confirm")

    return redirect("electricity_confirm")



'''
def electricity_payment(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")
    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    bill = request.session.get("ELECTRICITY_BILL", {})
    # print(f'{bill=}')

    
    if request.method == "POST":
        amount = request.POST.get("amount")
        tpin = request.POST.get("tpin")
        # print(f'{tpin=}')
      
        payload = {
            "amount": amount,
            'tpin':tpin,
            "biller_type": "Electricity",
            "return_payload": bill.get("return_payload", {})
        }
        # print(f"Payload: {payload}")

        try:
            res = requests.post(
                f"{Baseurl}/recharge-payment/",
                json=payload,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=20
            )
            # print(f'Response: {res}')
            data = res.json()
            # print("PAYMENT RESPONSE:", data)
            # ✅ SUCCESS CONDITION
            if (
                res.status_code == 200
                and data.get("status") is True
                and data.get("bill_data", {}).get("status") == "SUCCESS"
            ):

                # success_payload = data["data"]["payload"]
                success_payload = data["bill_data"]["payload"]
                # print(f'{success_payload=}')
                # ✅ CLEAR SESSION (NO DOUBLE PAYMENT)
                if "ELECTRICITY_BILL" in request.session:
                    del request.session["ELECTRICITY_BILL"]

                # Build receipt dictionary
                receipt = {
                    "customer_name": data.get("name", ""),
                    "amount": amount,
                    "Consumer_Id": bill.get("return_payload", {}).get("customerParams", {}).get("CUstomer ID Registration Number", ""),
                    "transaction_id": success_payload.get("additionalParams", {}).get("transactionID", ""),
                    "reference_id": success_payload.get("additionalParams", {}).get("txnReferenceId", ""),
                    "Outstanding_Amount": success_payload.get("additionalParams", {}).get("Total Outstanding Amount", ""),
                    "approval_ref": success_payload.get("reason", {}).get("approvalRefNum", ""),
                    "responseReason":success_payload.get("reason", {}).get("responseReason", ""),
                    "time": success_payload.get("timeStamp", ""),
                    "status": data.get("data", {}).get("status"),
                    # "status":bill.get("return_payload", {}).get("status", {}),
                    "mobile": data.get("mobile", ""),
                    "self_cashback": data.get("self_cashback", ""),
                    "biller_type": "Electricity",
                }
                # print(f'{receipt=}')

                return render(request, "electricity_bill/electricity_success.html", {
                    "message": data.get("message"),
                    "receipt": receipt,
                    "user_data": user_data
                })

                 # ❌ PAYMENT FAILED
            # return render(request, "recharge_fastag/fastag_confirm.html", {
            #     "Consumer_Id": bill.get("Consumer_Id", ""),
            #     "payload": bill.get("payload", {}),
            #     "error": data.get("message", "Payment Failed"),
            #     "user_data": user_data
            # })

            # ❌ PAYMENT FAILED
            error_message = (
                data.get("error", {})
                    .get("payload", {})
                    .get("errors", [{}])[0]
                    .get("reason")
                or data.get("message", "Payment Failed")
            )

            messages.error(request, error_message)
            # print(f'{messages=}')
            return redirect("electricity_confirm")


        except requests.RequestException as e:
            # print("REQUEST ERROR:", e)
            return render(request, "electricity_bill/electricity_confirm.html", {
                "Consumer_Id": bill.get("Consumer_Id", ""),
                "payload": bill.get("payload", {}),
                "error": "Server error. Please try again.",
                "user_data": user_data
            })
        except Exception as e:
            #print("GENERAL ERROR:", e)
            return render(request, "electricity_bill/electricity_confirm.html", {
                "Consumer_Id": bill.get("Consumer_Id", ""),
                "payload": bill.get("payload", {}),
                "error": "Server error. Please try again.",
                "user_data": user_data
            })



    return render(request, "electricity_bill/electricity_success.html", {
                "user_data": user_data,'access_token':access_token ,
            })

'''