from django.shortcuts import render, redirect
from django.contrib import messages
from lelifeproject.views import refresh_tokents
import requests
from datetime import datetime

Baseurl = "https://api.jinora.co.in/api"


# ================================================================================================
#                               Municiple Taxes - Category View
# ================================================================================================
def municiple_taxes_category_view(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    category = request.GET.get("category", "Muncipal Taxes")
    billers = []

    def taxes_category_data(token):
        return requests.get(
            f"{Baseurl}/npci/get-biller-by-category/",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            params={"category": category},
            timeout=10
        )

    response = taxes_category_data(access_token)
    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get("access_token")
            response = taxes_category_data(new_token)
        else:
            messages.error(request, "Session expired. Please login again.")
            return redirect("sign_in")
    try:
        data = response.json()
        # print(f'{data=}')
        if response.status_code == 200 and data.get("status"):
            billers = data.get("data", [])
        else:
            messages.error(request, "Unable to fetch billers from Municiple Taxes server.")
    except Exception:
        messages.error(request, "Invalid response from Municiple Taxes server.")

    return render(request, "municiple_taxes/municiple_taxes_billers.html", {
        "billers": billers,
        "category": category,
        "user_data": user_data
    })


# ================================================================================================
#                               Municiple Taxes - Fetch Bill
# ================================================================================================
def municiple_taxes_fetch_bill(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if request.method == "POST":
        Unique_Id_Code = request.POST.get("Unique_Id_Code")
        print(f'{Unique_Id_Code=}')
        billerId = request.POST.get("billerId")

        if not Unique_Id_Code :
            messages.error(request, "Please enter unique id code.")
            return redirect("municiple_taxes_fetch")

        def taxes_fetch_bill_data(token):
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return requests.post(
                f"{Baseurl}/npci/fetch-municipal-taxes-bill/",
                json={
                    "Unique_Id_Code": Unique_Id_Code,
                    "billerId": billerId
                },
                headers=headers,
                timeout=15
            )

        response = taxes_fetch_bill_data(access_token)
        print(f'{response=}')
        if response.status_code in (401, 403):
            if refresh_tokents(request):
                new_token = request.session.get("access_token")
                response = taxes_fetch_bill_data(new_token)
            else:
                messages.error(request, "Session expired. Please login again.")
                return redirect("sign_in")

        try:
            data = response.json()
            # print(f'{data=}')
            if response.status_code == 200 and data.get("status"):
                request.session["MUNICIPLE_TAXES_BILL"] = {
                    "Unique_Id_Code": Unique_Id_Code,
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                }
                return redirect("municiple_taxes_confirm")
            else:
                messages.error(request, "Unable to fetch Municiple Taxes bill")
                return redirect('municiple_taxes_fetch')
        except Exception:
            messages.error(request, "Invalid response from Municiple Taxes server.")
            return redirect('municiple_taxes_category')

    return render(request, "municiple_taxes/municiple_taxes_fetch.html", {
        "user_data": user_data
    })


# ================================================================================================
#                         Municiple Taxes - Confirm Bill View
# ================================================================================================
def municiple_taxes_bill_confirm(request):
    if "MUNICIPLE_TAXES_BILL" not in request.session:
        return redirect("municiple_taxes_category")

    bill = request.session.get("MUNICIPLE_TAXES_BILL", {})
    user_data = request.session.get("user_data", {})

    payload = bill.get("payload", {})
    context = {
        "Unique_Id_Code": bill.get("Unique_Id_Code"),
        "billerId": bill.get("billerId"),
        "payload": payload,
        "user_data": user_data,
    }
    return render(request, "municiple_taxes/municiple_taxes_confirm.html", context)


# ================================================================================================
#                         Municiple Taxes - Bill Payment
# ================================================================================================
def municiple_taxes_bill_payment(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if "MUNICIPLE_TAXES_BILL" not in request.session:
        return redirect("municiple_taxes_category")

    bill = request.session.get("MUNICIPLE_TAXES_BILL", {})
    def taxes_payment_api(token, payload):
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
            "biller_type": "Municiple Taxes",
            "return_payload": bill.get("return_payload", {})
        }

        try:
            res = taxes_payment_api(access_token, payload)
            if res.status_code in (401, 403):
                if refresh_tokents(request):
                    access_token = request.session.get("access_token")
                    res = taxes_payment_api(access_token, payload)
                else:
                    messages.error(request, "Session expired. Please login again.")
                    return redirect("sign_in")

            data = res.json()
            if (
                res.status_code == 200
                and data.get("status") is True
                and data.get("bill_data", {}).get("status") == "SUCCESS"
            ):
                success_payload = data["bill_data"]["payload"]
                raw_time = success_payload.get("timeStamp")
                formatted_time = ""

                if raw_time:
                    clean_time = raw_time.split("+")[0]
                    formatted_time = datetime.strptime(
                        clean_time, "%Y-%m-%dT%H:%M:%S"
                    ).strftime("%d %b %Y, %I:%M %p")

                request.session.pop("MUNICIPLE_TAXES_BILL", None)

                receipt = {
                    "customer_name": data.get("name", ""),
                    "amount": amount,
                    "refid": success_payload.get("refId", ""),

                    "time": formatted_time,

                     # TRANSACTION
                    "transaction_id": success_payload.get("additionalParams", {}).get("transactionID", ""),
                    "reference_id": success_payload.get("additionalParams", {}).get("txnReferenceId", ""),
                    "biller_reference_number": success_payload.get("additionalParams", {}).get("billerReferenceNumber", ""),

                    # RESPONSE
                    "approval_ref": success_payload.get("reason", {}).get("approvalRefNum", ""),
                    "responseCode": success_payload.get("reason", {}).get("responseCode", ""),
                    "responseReason": success_payload.get("reason", {}).get("responseReason", ""),
                    "mobile": data.get("mobile", ""),
                    "self_cashback": data.get("self_cashback", ""),
                    "biller_type": "Municiple Taxes",
                }
                print(f'{receipt=}')

                return render(request, "municiple_taxes/municiple_taxes_success.html", {
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
            return redirect("municiple_taxes_confirm")

        except requests.RequestException:
            messages.error(request, "Server error. Please try again.")
            return redirect("municiple_taxes_confirm")

    return redirect("municiple_taxes_confirm")
