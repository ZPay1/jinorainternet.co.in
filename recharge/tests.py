from urllib import request
from django.shortcuts import get_object_or_404, render
from django.shortcuts import render
# from .models import Service
from django.shortcuts import render, redirect
from django.contrib import messages
# Create your views here.
import requests
Baseurl = "https://api.jinora.co.in/api"


def fastag_category_view(request):
    user_data = request.session.get("user_data", {})
    if 'user_data' not in request.session:
        return redirect('sign_in')

    category = request.GET.get("category", "Fastag")
    access_token = request.session["user_data"]["access"]

    billers = []
    try:
        res = requests.get(
            f"{Baseurl}/npci/get-biller-by-category/",
            headers={"Authorization": f"Bearer {access_token}"},
            params={"category": category},
            timeout=10
        )
        if res.ok and res.json().get("status"):
            billers = res.json()["data"]
    except Exception:
        pass

    return render(request, "recharge/fastag_billers.html", {
        "billers": billers,
        "category": category,
        'user_data':user_data
    })


def fastag_fetch_bill(request):
    user_data = request.session.get("user_data", {})
    if 'user_data' not in request.session:
        return redirect('sign_in')

    access_token = request.session["user_data"]["access"]

    if request.method == "POST":
        vehicle_number = request.POST.get("vehicle_number")
        billerId = request.POST.get("billerId") 

        try:
            res = requests.post(
                f"{Baseurl}/npci/fetch-fastag-bill/",
                json={"vehicle_number": vehicle_number, "billerId": billerId},
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=15
            )

            data = res.json()
            # #print(f'========================={data=}')
            if res.ok and data.get("status"):
                # #print(f'{data["data"]["payload"]=}')
                # #print(f"{data["return_payload"]=}")
                # 🔐 STORE IN SESSION (CRITICAL)
                request.session["FASTAG_BILL"] = {
                    "vehicle_number": vehicle_number,
                    "billerId": billerId,
                    "payload": data["data"]["payload"],
                    "return_payload": data["return_payload"]
                }

                return redirect("fastag_confirm")

        except Exception:
            pass

    return render(request, "recharge/fastag_fetch.html",{'user_data':user_data})

def fastag_confirm(request):
    # 🔐 Session safety
    if "FASTAG_BILL" not in request.session:
        return redirect("fastag_fetch")

    bill = request.session.get("FASTAG_BILL", {})
    user_data = request.session.get("user_data", {})

    payload = bill.get("payload", {})
    biller_response = payload.get("billerResponse", {})
    additional_params = payload.get("additionalParams", {})

    # 🔥 Normalize additionalParams (SPACE → SAFE KEYS)
    additional = {
        "tag_status": additional_params.get("Tag Status"),
        "max_amount": additional_params.get("Maximum Permissible Recharge Amount"),
        "wallet_balance": additional_params.get("Wallet Balance"),
    }

    context = {
        "vehicle_number": bill.get("vehicle_number"),
        "billerId": bill.get("billerId"),

        # original payload
        "payload": payload,

        # extracted helpers
        "biller": biller_response,
        "additional": additional,

        # user
        "user_data": user_data,
    }

    return render(request, "recharge/fastag_confirm.html", context)

# def fastag_confirm(request):
#     if "FASTAG_BILL" not in request.session:
#         return redirect("fastag_fetch")
#     user_data = request.session.get('user_data', {})    

#     bill = request.session["FASTAG_BILL"]
    

#     return render(request, "recharge/fastag_confirm.html", {
#         "vehicle_number": bill.get("vehicle_number"),
#         "billerId": bill.get("billerId"),
#         "payload": bill.get("payload"),
#         'user_data':user_data
#     })

def fastag_payment(request):
    if "FASTAG_BILL" not in request.session:
        return redirect("fastag_fetch")

    user_data = request.session.get("user_data", {})
    access_token = user_data.get("access")
    bill = request.session.get("FASTAG_BILL", {})

    if request.method == "POST":
        amount = request.POST.get("amount")

        payload = {
            "amount": amount,
            "return_payload": bill.get("return_payload", {})
        }
        #print(f"Payload: {payload}")

        try:
            res = requests.post(
                f"{Baseurl}/npci/bill-payment/",
                json=payload,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=20
            )
            #print(f'Response: {res}')
            data = res.json()
            #print("PAYMENT RESPONSE:", data)

            # ✅ SUCCESS CONDITION
            if (
                res.status_code == 200
                and data.get("status") is True
                and data.get("data", {}).get("status") == "SUCCESS"
            ):
                success_payload = data["data"]["payload"]

                # ✅ CLEAR SESSION (NO DOUBLE PAYMENT)
                if "FASTAG_BILL" in request.session:
                    del request.session["FASTAG_BILL"]

                # Build receipt dictionary
                receipt = {
                    "customer_name": bill.get("return_payload", {}).get("customerDetails", {}).get("EMAIL", ""),
                    "amount": amount,
                    "vehicle_number": bill.get("return_payload", {}).get("customerParams", {}).get("Vehicle Registration Number", ""),
                    "transaction_id": success_payload.get("additionalParams", {}).get("transactionID", ""),
                    "reference_id": success_payload.get("additionalParams", {}).get("txnReferenceId", ""),
                    "approval_ref": success_payload.get("reason", {}).get("approvalRefNum", ""),
                    "time": success_payload.get("timeStamp", ""),
                    "status": data.get("data", {}).get("status"),
                    "mobile": bill.get("return_payload", {}).get("customerMobileNumber", ""),
                    "biller_type": "FASTAG",
                }

                return render(request, "recharge/fastag_success.html", {
                    "message": data.get("message"),
                    "receipt": receipt,
                    "user_data": user_data
                })

            # ❌ PAYMENT FAILED
            return render(request, "recharge/fastag_confirm.html", {
                "vehicle_number": bill.get("vehicle_number", ""),
                "payload": bill.get("payload", {}),
                "error": data.get("message", "Payment Failed"),
                "user_data": user_data
            })

        except requests.RequestException as e:
            #print("REQUEST ERROR:", e)
            return render(request, "recharge/fastag_confirm.html", {
                "vehicle_number": bill.get("vehicle_number", ""),
                "payload": bill.get("payload", {}),
                "error": "Server error. Please try again.",
                "user_data": user_data
            })
        except Exception as e:
            #print("GENERAL ERROR:", e)
            return render(request, "recharge/fastag_confirm.html", {
                "vehicle_number": bill.get("vehicle_number", ""),
                "payload": bill.get("payload", {}),
                "error": "Server error. Please try again.",
                "user_data": user_data
            })
