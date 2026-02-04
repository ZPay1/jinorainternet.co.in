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
def landline_postpaid_category_view(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    category = request.GET.get("category", "Landline Postpaid")
    billers = []

    def landline_category_data(token):
        return requests.get(
            f"{Baseurl}/npci/get-biller-by-category/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            params={"category": category},
            timeout=10
        )

    response = landline_category_data(access_token)
    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get("access_token")
            response = landline_category_data(new_token)
        else:
            messages.error(request, "Session expired. Please login again.")
            return redirect("sign_in")
    try:
        data = response.json()
        if response.status_code == 200 and data.get("status"):
            billers = data.get("data", [])
        else:
            messages.error(request, "Unable to fetch billers from Landline Postpaid server.")
    except Exception:
        messages.error(request, "Invalid response from Landline Postpaid server.")

    # Note: update template path as needed
    return render(request, "landline_postpaid/landline_postpaid_billers.html", {
        "billers": billers,
        "category": category,
        "user_data": user_data
    })

'''
===============================================================================================================
                        Fetch Bill method
===============================================================================================================
'''


def landline_postpaid_fetch_bill(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if request.method == "POST":
        Telephone_Number = request.POST.get("Telephone_Number")
        Account_Number = request.POST.get("Account_Number")
        
        billerId = request.POST.get("billerId")

        print(f'{Telephone_Number=}')
        
        # print(f'{billerId=}')

        if not Telephone_Number or not Account_Number:
            messages.error(request, "Please enter both Telephone Number and Account Number.")
            return redirect("landline_postpaid_fetch")

        def landline_fetch_bill_data(token):
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return requests.post(
                f"{Baseurl}/npci/fetch-landline_postpaid-bill/",
                json={
                    "Telephone_Number": Telephone_Number,
                    'Account_Number':Account_Number,
                    "billerId": billerId
                },
                headers=headers,
                timeout=15
            )

        response = landline_fetch_bill_data(access_token)
        print(f'{response=}')
        if response.status_code in (401, 403):
            if refresh_tokents(request):
                new_token = request.session.get("access_token")
                response = landline_fetch_bill_data(new_token)
            else:
                messages.error(request, "Session expired. Please login again.")
                return redirect("sign_in")

        try:
            data = response.json()
            print(f"{data=}")
            if response.status_code == 200 and data.get("status"):
                print({
                    "Telephone_Number": Telephone_Number,
                    "Account_Number": Account_Number,
                    
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                })
                request.session["LANDLINE_POSTPAID_BILL"] = {
                    "Telephone_Number": Telephone_Number,
                    "Account_Number": Account_Number,
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                }
                return redirect("landline_postpaid_confirm")
            else:
                messages.error(request, "Unable to fetch Landline Postpaid bill")
          
        except Exception:
            messages.error(request, "Invalid response from Landline Postpaid server.")
            return redirect('landline_postpaid_category')
    # Note: update template path as needed
    return render(request, "landline_postpaid/landline_postpaid_fetch.html", {
        "user_data": user_data
    })

'''
===============================================================================================================
                        Confirm method
===============================================================================================================
'''

def landline_postpaid_bill_confirm(request):
    if "LANDLINE_POSTPAID_BILL" not in request.session:
        return redirect("landline_postpaid_category")

    bill = request.session.get("LANDLINE_POSTPAID_BILL", {})
    user_data = request.session.get("user_data", {})

    payload = bill.get("payload", {})

    context = {
        "Telephone_Number": bill.get("Telephone_Number"),
        "Account_Number": bill.get("Account_Number"),
        
        "billerId": bill.get("billerId"),
        "payload": payload,
        "user_data": user_data,
    }

    # Note: update template path as needed
    return render(request, "landline_postpaid/landline_postpaid_confirm.html", context)

'''
===============================================================================================================
                       Payment method
===============================================================================================================
'''

from datetime import datetime
def landline_postpaid_payment(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if "LANDLINE_POSTPAID_BILL" not in request.session:
        return redirect("landline_postpaid_category")

    bill = request.session.get("LANDLINE_POSTPAID_BILL", {})
    def landline_payment_api(token, payload):
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
            "biller_type": "Landline Postpaid",
            "return_payload": bill.get("return_payload", {})
        }

        try:
            res = landline_payment_api(access_token, payload)
            print(f'{res=}')
            if res.status_code in (401, 403):
                if refresh_tokents(request):
                    access_token = request.session.get("access_token")
                    res = landline_payment_api(access_token, payload)
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
                request.session.pop("LANDLINE_POSTPAID_BILL", None)

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
                    "biller_type": "Landline Postpaid",
                }

                # Note: update template path as needed
                return render(request, "landline_postpaid/landline_postpaid_success.html", {
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
            return redirect("landline_postpaid_confirm")

        except requests.RequestException:
            messages.error(request, "Server error. Please try again.")
            return redirect("landline_postpaid_confirm")

    return redirect("landline_postpaid_confirm")
