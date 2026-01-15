from django.shortcuts import render, redirect
from django.contrib import messages
from lelifeproject.views import refresh_tokents
import requests

Baseurl = "https://api.jinora.co.in/api"

'''
===============================================================================================================
                        Category method (for Cable TV: cable_tv_category_view)
===============================================================================================================
'''
def cable_tv_category_view(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    category = request.GET.get("category", "Cable TV")
    billers = []

    def cable_tv_category_data(token):
        return requests.get(
            f"{Baseurl}/npci/get-biller-by-category/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            params={"category": category},
            timeout=10
        )

    response = cable_tv_category_data(access_token)
    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get("access_token")
            response = cable_tv_category_data(new_token)
        else:
            messages.error(request, "Session expired. Please login again.")
            return redirect("sign_in")
    try:
        data = response.json()
        if response.status_code == 200 and data.get("status"):
            billers = data.get("data", [])
        else:
            messages.error(request, "Unable to fetch billers from Cable TV server.")
    except Exception:
        messages.error(request, "Invalid response from Cable TV server.")
        return redirect('cable_tv_category')

    return render(request, "cable_tv/cable_tv_billers.html", {
        "billers": billers,
        "category": category,
        "user_data": user_data
    })

'''
===============================================================================================================
                        Fetch Bill method (for Cable TV: cable_tv_fetch_bill)
===============================================================================================================
'''
def cable_tv_fetch_bill(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if request.method == "POST":
        Customer_Id = request.POST.get("Customer_Id")
        billerId = request.POST.get("billerId")

        if not Customer_Id:
            messages.error(request, "Please enter subscriber ID.")
            return redirect("cable_tv_fetch")

        def cable_tv_fetch_bill_data(token):
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return requests.post(
                f"{Baseurl}/npci/fetch-cable-tv-bill/",
                json={
                    "Customer_Id": Customer_Id,
                    "billerId": billerId
                },
                headers=headers,
                timeout=15
            )

        response = cable_tv_fetch_bill_data(access_token)
        if response.status_code in (401, 403):
            if refresh_tokents(request):
                new_token = request.session.get("access_token")
                response = cable_tv_fetch_bill_data(new_token)
            else:
                messages.error(request, "Session expired. Please login again.")
                return redirect("sign_in")

        try:
            data = response.json()
            if response.status_code == 200 and data.get("status"):
                request.session["CABLE_TV_BILL"] = {
                    "Customer_Id": Customer_Id,
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                }
                return redirect("cable_tv_confirm")
            else:
                messages.error(request, "Unable to fetch Cable TV bill")
                return redirect('cable_tv_fetch')
        except Exception:
            messages.error(request, "Invalid response from Cable TV server.")

    return render(request, "cable_tv/cable_tv_fetch.html", {
        "user_data": user_data
    })

'''
===============================================================================================================
                        Confirm method (for Cable TV: cable_tv_bill_confirm)
===============================================================================================================
'''
def cable_tv_bill_confirm(request):
    if "CABLE_TV_BILL" not in request.session:
        return redirect("cable_tv_category")

    bill = request.session.get("CABLE_TV_BILL", {})
    user_data = request.session.get("user_data", {})

    payload = bill.get("payload", {})
    context = {
        "Customer_Id": bill.get("Customer_Id"),
        "billerId": bill.get("billerId"),
        "payload": payload,
        "user_data": user_data,
    }
    return render(request, "cable_tv/cable_tv_confirm.html", context)

'''
===============================================================================================================
                       Payment method (for Cable TV: cable_tv_bill_payment)
===============================================================================================================
'''
from datetime import datetime
def cable_tv_bill_payment(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if "CABLE_TV_BILL" not in request.session:
        return redirect("cable_tv_category")

    bill = request.session.get("CABLE_TV_BILL", {})
    def cable_tv_payment_api(token, payload):
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
            "biller_type": "Cable TV",
            "return_payload": bill.get("return_payload", {})
        }

        try:
            res = cable_tv_payment_api(access_token, payload)
            if res.status_code in (401, 403):
                if refresh_tokents(request):
                    access_token = request.session.get("access_token")
                    res = cable_tv_payment_api(access_token, payload)
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

                request.session.pop("CABLE_TV_BILL", None)

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
                    "biller_type": "Cable TV",
                    
                }

                return render(request, "cable_tv/cable_tv_success.html", {
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
            return redirect("cable_tv_confirm")

        except requests.RequestException:
            messages.error(request, "Server error. Please try again.")
            return redirect("cable_tv_confirm")

    return redirect("cable_tv_confirm")
