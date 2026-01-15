from django.shortcuts import render, redirect
from django.contrib import messages
from lelifeproject.views import refresh_tokents
import requests

Baseurl = "https://api.jinora.co.in/api"

'''
===============================================================================================================
                        Category method (for Hospital: hospital_category_view)
===============================================================================================================
'''
def hospital_category_view(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    category = request.GET.get("category", "Hospital")
    billers = []

    def hospital_category_data(token):
        return requests.get(
            f"{Baseurl}/npci/get-biller-by-category/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            params={"category": category},
            timeout=10
        )

    response = hospital_category_data(access_token)
    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get("access_token")
            response = hospital_category_data(new_token)
        else:
            messages.error(request, "Session expired. Please login again.")
            return redirect("sign_in")
    try:
        data = response.json()
        if response.status_code == 200 and data.get("status"):
            billers = data.get("data", [])
        else:
            messages.error(request, "Unable to fetch billers from Hospital server.")
    except Exception:
        messages.error(request, "Invalid response from Hospital server.")
        return redirect('municiple_taxes_category')
    return render(request, "hospital/hospital_billers.html", {
        "billers": billers,
        "category": category,
        "user_data": user_data
    })

'''
===============================================================================================================
                        Fetch Bill method (for Hospital: hospital_fetch_bill)
===============================================================================================================
'''
def hospital_fetch_bill(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if request.method == "POST":
        Registered_Mobile_Number = request.POST.get("Registered_Mobile_Number")
        billerId = request.POST.get("billerId")

        if not Registered_Mobile_Number:
            messages.error(request, "Please enter Registered Mobile Number.")
            return redirect("hospital_fetch")

        def hospital_fetch_bill_data(token):
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return requests.post(
                f"{Baseurl}/npci/fetch-hospital-bill/",
                json={
                    "Registered_Mobile_Number": Registered_Mobile_Number,
                    "billerId": billerId
                },
                headers=headers,
                timeout=15
            )

        response = hospital_fetch_bill_data(access_token)
        if response.status_code in (401, 403):
            if refresh_tokents(request):
                new_token = request.session.get("access_token")
                response = hospital_fetch_bill_data(new_token)
            else:
                messages.error(request, "Session expired. Please login again.")
                return redirect("sign_in")

        try:
            data = response.json()
            if response.status_code == 200 and data.get("status"):
                request.session["HOSPITAL_BILL"] = {
                    "Registered_Mobile_Number": Registered_Mobile_Number,
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                }
                return redirect("hospital_confirm")
            else:
                messages.error(request, "Unable to fetch Hospital bill")
                return redirect('hospital_fetch')
        except Exception:
            messages.error(request, "Invalid response from Hospital server.")

    return render(request, "hospital/hospital_fetch.html", {
        "user_data": user_data
    })

'''
===============================================================================================================
                        Confirm method (for Hospital: hospital_bill_confirm)
===============================================================================================================
'''
def hospital_bill_confirm(request):
    if "HOSPITAL_BILL" not in request.session:
        return redirect("hospital_category")

    bill = request.session.get("HOSPITAL_BILL", {})
    user_data = request.session.get("user_data", {})

    payload = bill.get("payload", {})
    context = {
        "Registered_Mobile_Number": bill.get("Registered_Mobile_Number"),
        "billerId": bill.get("billerId"),
        "payload": payload,
        "user_data": user_data,
    }
    return render(request, "hospital/hospital_confirm.html", context)

'''
===============================================================================================================
                       Payment method (for Hospital: hospital_bill_payment)
===============================================================================================================
'''
from datetime import datetime
def hospital_bill_payment(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if "HOSPITAL_BILL" not in request.session:
        return redirect("hospital_category")

    bill = request.session.get("HOSPITAL_BILL", {})
    def hospital_payment_api(token, payload):
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
            "biller_type": "Hospital",
            "return_payload": bill.get("return_payload", {})
        }

        try:
            res = hospital_payment_api(access_token, payload)
            if res.status_code in (401, 403):
                if refresh_tokents(request):
                    access_token = request.session.get("access_token")
                    res = hospital_payment_api(access_token, payload)
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
                    # Remove timezone
                    clean_time = raw_time.split("+")[0]
                    formatted_time = datetime.strptime(
                        clean_time, "%Y-%m-%dT%H:%M:%S"
                    ).strftime("%d %b %Y, %I:%M %p")

                request.session.pop("HOSPITAL_BILL", None)

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
                    "status": data.get("data", {}).get("status"),
                    "mobile": data.get("mobile", ""),
                    "self_cashback": data.get("self_cashback", ""),
                    "biller_type": "Hospital",
                }

                return render(request, "hospital/hospital_success.html", {
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
            return redirect("hospital_confirm")

        except requests.RequestException:
            messages.error(request, "Server error. Please try again.")
            return redirect("hospital_confirm")

    return redirect("hospital_confirm")
