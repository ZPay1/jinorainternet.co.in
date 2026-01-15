from django.shortcuts import render, redirect
from django.contrib import messages
from lelifeproject.views import refresh_tokents
import requests

Baseurl = "https://api.jinora.co.in/api"

'''
===============================================================================================================
                        Category method (for Health Insurance: health_insurance_category_view)
===============================================================================================================
'''

def health_insurance_category_view(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    category = request.GET.get("category", "Health Insurance")
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

    response = insurance_category_data(access_token)
    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get("access_token")
            response = insurance_category_data(new_token)
        else:
            messages.error(request, "Session expired. Please login again.")
            return redirect("sign_in")
    try:
        data = response.json()
        if response.status_code == 200 and data.get("status"):
            billers = data.get("data", [])
        else:
            messages.error(request, "Unable to fetch billers from Health Insurance server.")
    except Exception:
        messages.error(request, "Invalid response from Health Insurance server.")
        return redirect('health_insurance_category')
    return render(request, "health_insurance/health_insurance_billers.html", {
        "billers": billers,
        "category": category,
        "user_data": user_data
    })


'''
===============================================================================================================
                        Fetch Bill method (for Health Insurance: health_insurance_fetch_bill)
===============================================================================================================
'''
def health_insurance_fetch_bill(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if request.method == "POST":
        Policy_Number = request.POST.get("Policy_Number")
        Customer_Mobile_Number = request.POST.get("Customer_Mobile_Number")
        billerId = request.POST.get("billerId")

        if not Policy_Number or not Customer_Mobile_Number:
            messages.error(request, "Please enter both Policy Number and Customer Mobile Number.")
            return redirect("health_insurance_fetch")

        def insurance_fetch_bill_data(token):
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return requests.post(
                f"{Baseurl}/npci/fetch-health-insurance-bill/",
                json={
                    "Policy_Number": Policy_Number,
                    "Customer_Mobile_Number": Customer_Mobile_Number,
                    "billerId": billerId
                },
                headers=headers,
                timeout=15
            )

        response = insurance_fetch_bill_data(access_token)
        if response.status_code in (401, 403):
            if refresh_tokents(request):
                new_token = request.session.get("access_token")
                response = insurance_fetch_bill_data(new_token)
            else:
                messages.error(request, "Session expired. Please login again.")
                return redirect("sign_in")

        try:
            data = response.json()
            if response.status_code == 200 and data.get("status"):
                request.session["HEALTH_INSURANCE_BILL"] = {
                    "Policy_Number": Policy_Number,
                    "Customer_Mobile_Number": Customer_Mobile_Number,
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                }
                return redirect("health_insurance_confirm")
            else:
                messages.error(request, "Unable to fetch Health Insurance bill")
                return redirect('health_insurance_fetch')
        except Exception:
            messages.error(request, "Invalid response from Health Insurance server.")

    return render(request, "health_insurance/health_insurance_fetch.html", {
        "user_data": user_data
    })


'''
===============================================================================================================
                        Confirm method (for Health Insurance: health_insurance_bill_confirm)
===============================================================================================================
'''
def health_insurance_bill_confirm(request):
    if "HEALTH_INSURANCE_BILL" not in request.session:
        return redirect("health_insurance_category")

    bill = request.session.get("HEALTH_INSURANCE_BILL", {})
    # print(f'{bill=}')
    user_data = request.session.get("user_data", {})

    payload = bill.get("payload", {})
    context = {
        "Policy_Number": bill.get("Policy_Number"),
        "Customer_Mobile_Number": bill.get("Customer_Mobile_Number"),
        "billerId": bill.get("billerId"),
        "payload": payload,
        "user_data": user_data,
    }
    # print(f'rrrrrrrrrrr{context=}')
    return render(request, "health_insurance/health_insurance_confirm.html", context)


'''
===============================================================================================================
                       Payment method (for Health Insurance: health_insurance_bill_payment)
===============================================================================================================
'''
from datetime import datetime


def health_insurance_bill_payment(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if "HEALTH_INSURANCE_BILL" not in request.session:
        return redirect("health_insurance_category")

    bill = request.session.get("HEALTH_INSURANCE_BILL", {})
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
        amount = request.POST.get("amount")
        tpin = request.POST.get("tpin")

        payload = {
            "amount": amount,
            "tpin": tpin,
            "biller_type": "Health Insurance",
            "return_payload": bill.get("return_payload", {})
        }

        try:
            res = insurance_payment_api(access_token, payload)
            if res.status_code in (401, 403):
                if refresh_tokents(request):
                    access_token = request.session.get("access_token")
                    res = insurance_payment_api(access_token, payload)
                else:
                    messages.error(request, "Session expired. Please login again.")
                    return redirect("sign_in")

            data = res.json()
            # print(f'{data=}')
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

                receipt = {
                    "customer_name": data.get("name", ""),
                    "amount": amount,
                    "refid": success_payload.get("refId", ""),

                    "time": formatted_time,

                     # 🔹 TRANSACTION
                    "transaction_id": success_payload.get("additionalParams", {}).get("transactionID", ""),
                    "reference_id": success_payload.get("additionalParams", {}).get("txnReferenceId", ""),
                    "biller_reference_number": success_payload.get("additionalParams", {}).get("billerReferenceNumber", ""),

                    # 🔹 RESPONSE
                    "approval_ref": success_payload.get("reason", {}).get("approvalRefNum", ""),
                    "responseCode": success_payload.get("reason", {}).get("responseCode", ""),
                    "responseReason": success_payload.get("reason", {}).get("responseReason", ""),
                    "mobile": data.get("mobile", ""),
                    "self_cashback": data.get("self_cashback", ""),
                    "biller_type": "Health Insurance",
                }
                print(f'{receipt=}')

                return render(request, "health_insurance/health_insurance_success.html", {
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
            return redirect("health_insurance_confirm")

        except requests.RequestException:
            messages.error(request, "Server error. Please try again.")
            return redirect("health_insurance_confirm")

    return redirect("health_insurance_confirm")
