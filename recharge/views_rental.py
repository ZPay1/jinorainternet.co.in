from django.shortcuts import render, redirect
from django.contrib import messages
from lelifeproject.views import refresh_tokents
import requests

from django.conf import settings
Baseurl = f"{settings.JINORA_API_BASE}"

'''
===============================================================================================================
                        Category method (for Rental: rental_category_view)
===============================================================================================================
'''
def rental_category_view(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    category = request.GET.get("category", "Rental")
    billers = []

    def rental_category_data(token):
        return requests.get(
            f"{Baseurl}/npci/get-biller-by-category/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            params={"category": category},
            timeout=10
        )

    response = rental_category_data(access_token)
    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get("access_token")
            response = rental_category_data(new_token)
        else:
            messages.error(request, "Session expired. Please login again.")
            return redirect("sign_in")
    try:
        data = response.json()
        if response.status_code == 200 and data.get("status"):
            billers = data.get("data", [])
        else:
            messages.error(request, "Unable to fetch billers from Rental server.")
    except Exception:
        messages.error(request, "Invalid response from Rental server.")

    return render(request, "rental/rental_billers.html", {
        "billers": billers,
        "category": category,
        "user_data": user_data
    })

'''
===============================================================================================================
                        Fetch Bill method (for Rental: rental_fetch_bill)
===============================================================================================================
'''
def rental_fetch_bill(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if request.method == "POST":
        Bill_Invoice_No = request.POST.get("Bill_Invoice_No")
        billerId = request.POST.get("billerId")

        if not Bill_Invoice_No:
            messages.error(request, "Please enter Bill Invoice number etc.")
            return redirect("rental_fetch")

        def rental_fetch_bill_data(token):
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return requests.post(
                f"{Baseurl}/npci/fetch-rental-bill/",
                json={
                 
                    "Bill_Invoice_No": Bill_Invoice_No,
                    "billerId": billerId
                },
                headers=headers,
                timeout=15
            )

        response = rental_fetch_bill_data(access_token)
        if response.status_code in (401, 403):
            if refresh_tokents(request):
                new_token = request.session.get("access_token")
                response = rental_fetch_bill_data(new_token)
            else:
                messages.error(request, "Session expired. Please login again.")
                return redirect("sign_in")

        try:
            data = response.json()
            if response.status_code == 200 and data.get("status"):
                request.session["RENTAL_BILL"] = {
                    "Bill_Invoice_No": Bill_Invoice_No,
                
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                }
                return redirect("rental_confirm")
            else:
                messages.error(request, "Unable to fetch Rental bill")
                return redirect('rental_fetch')
        except Exception:
            messages.error(request, "Invalid response from Rental server.")

    return render(request, "rental/rental_fetch.html", {
        "user_data": user_data
    })

'''
===============================================================================================================
                        Confirm method (for Rental: rental_bill_confirm)
===============================================================================================================
'''
def rental_bill_confirm(request):
    if "RENTAL_BILL" not in request.session:
        return redirect("rental_category")

    bill = request.session.get("RENTAL_BILL", {})
    user_data = request.session.get("user_data", {})

    payload = bill.get("payload", {})
    context = {
        "Bill_Invoice_No": bill.get("Bill_Invoice_No"),
    
        "billerId": bill.get("billerId"),
        "payload": payload,
        "user_data": user_data,
    }
    return render(request, "rental/rental_confirm.html", context)

'''
===============================================================================================================
                       Payment method (for Rental: rental_bill_payment)
===============================================================================================================
'''
from datetime import datetime
def rental_bill_payment(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if "RENTAL_BILL" not in request.session:
        return redirect("rental_category")

    bill = request.session.get("RENTAL_BILL", {})
    def rental_payment_api(token, payload):
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
            "biller_type": "Rental",
            "return_payload": bill.get("return_payload", {})
        }

        try:
            res = rental_payment_api(access_token, payload)
            if res.status_code in (401, 403):
                if refresh_tokents(request):
                    access_token = request.session.get("access_token")
                    res = rental_payment_api(access_token, payload)
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
                request.session.pop("RENTAL_BILL", None)

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
                    # "time": success_payload.get("timeStamp", ""),
                    "status": data.get("data", {}).get("status"),
                    "mobile": data.get("mobile", ""),
                    "self_cashback": data.get("self_cashback", ""),
                    "biller_type": "Rental",
                }

                return render(request, "rental/rental_success.html", {
                    "message": data.get("message"),
                    "receipt": receipt,
                    "user_data": user_data
                })

            error_message = (
                data.get("error", {})
                    .get("payload", {})
                    .get("errors", [{}])[0]
                    .get("errorDtl")
                or data.get("message", "Payment Failed")
            )

            messages.error(request, error_message)
            return redirect("rental_confirm")

        except requests.RequestException:
            messages.error(request, "Server error. Please try again.")
            return redirect("rental_confirm")

    return redirect("rental_confirm")
