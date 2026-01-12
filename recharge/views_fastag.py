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
def fastag_category_view(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    category = request.GET.get("category", "Fastag")
    billers = []

    def fastag_category_data(token):
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
    response = fastag_category_data(access_token)
    #print(f'{response=}')
    # 🔁 Step 2: Token expired → refresh → retry
    if response.status_code in (401, 403):
        if refresh_tokents(request):
            new_token = request.session.get("access_token")
            response = fastag_category_data(new_token)
        else:
            messages.error(request, "Session expired. Please login again.")
            return redirect("sign_in")

    try:
        # ✅ Parse response safely
        data = response.json()
        #print(f"{data=}")

        if response.status_code == 200 and data.get("status"):
            billers = data.get("data", [])
            #print(f'{billers=}')
        else:
            messages.error(request, "Unable to fetch billers from FASTag server.")

    except Exception:
        messages.error(request, "Invalid response from FASTag server.")

    return render(request, "recharge_fastag/fastag_billers.html", {
        "billers": billers,
        "category": category,
        "user_data": user_data
    })

# def fastag_category_view(request):
#     user_data = request.session.get("user_data", {})
#     access_token = request.session.get("access_token")

#     if not access_token:
#         messages.error(request, "Session expired. Please sign in again.")
#         return redirect("sign_in") 

#     category = request.GET.get("category", "Fastag")


#     billers = []

#     def fastag_category_data(token):
#         return requests.get(
#             f"{Baseurl}/npci/get-biller-by-category/",
#             headers={
#                 "Authorization": f"Bearer {token}",
#                 "Content-Type": "application/json"
#             },
#             params={"category": category},
#             timeout=10
#         )

#     response = fastag_category_data(access_token)
#     #print(f'{response=}')
#     # 🔁 Token expire case
#     if response.status_code in (401, 403):
#         if refresh_tokents(request):
#             new_token = request.session.get('access_token')
#             response = fastag_category_data(new_token)
#         else:
#             return redirect('sign_in')

#     # ✅ Success response
#     try:
#         if response.status_code == 200:
#             data = response.json()
#             #print(f'{data=}')
#             if data.get("status"):
#                 billers = data.get("data", [])
#     except Exception as e:
#         messages.error(request, f"API request failed: {str(e)}")
#         return redirect('sign_in')

#     return render(request, "recharge_fastag/fastag_billers.html", {
#         "billers": billers,
#         "category": category,
#         "user_data": user_data
#     })




'''
===============================================================================================================
                        Fetch bIll method
===============================================================================================================
'''
def fastag_fetch_bill(request):
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")

    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    if request.method == "POST":
        vehicle_number = request.POST.get("vehicle_number")
        billerId = request.POST.get("billerId")

        if not vehicle_number or not billerId:
            messages.error(request, "Please enter vehicle number.")
            return redirect("fastag_fetch")

        def fetch_fastag_bill(token):
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            return requests.post(
                f"{Baseurl}/npci/fetch-fastag-bill/",
                json={
                    "vehicle_number": vehicle_number,
                    "billerId": billerId
                },
                headers=headers,
                timeout=15
            )

        # 🔁 Step 1: First API call
        response = fetch_fastag_bill(access_token)
        #print(f'{response=}')
        # 🔁 Step 2: Token expired → refresh → retry
        if response.status_code in (401, 403):
            if refresh_tokents(request):
                new_token = request.session.get("access_token")
                response = fetch_fastag_bill(new_token)
            else:
                messages.error(request, "Session expired. Please login again.")
                return redirect("sign_in")

        try:
            data = response.json()
            #print(f"{data=}")

            if response.status_code == 200 and data.get("status"):
                # 🔐 Store bill data in session
                request.session["FASTAG_BILL"] = {
                    "vehicle_number": vehicle_number,
                    "billerId": billerId,
                    "payload": data.get("data", {}).get("payload"),
                    "return_payload": data.get("return_payload"),
                }
                return redirect("fastag_confirm")

            else:
                messages.error(request, "Unable to fetch FASTag bill")

        except Exception:
            messages.error(request, "Invalid response from FASTag server.")

    return render(request, "recharge_fastag/fastag_fetch.html", {
        "user_data": user_data
    })

# def fastag_fetch_bill(request):
#     user_data = request.session.get("user_data", {})
#     access_token = request.session.get("access_token")


#     if not access_token:
#         messages.error(request, "Session expired. Please sign in again.")
#         return redirect("sign_in") 

#     if request.method == "POST":
#         vehicle_number = request.POST.get("vehicle_number")
#         billerId = request.POST.get("billerId")

#         def fetch_fastag_bill(token):
#             headers={
#                     "Authorization": f"Bearer {token}",
#                     "Content-Type": "application/json"
#                 }
#             return requests.post(
#                 f"{Baseurl}/npci/fetch-fastag-bill/",
#                 json={
#                     "vehicle_number": vehicle_number,
#                     "billerId": billerId
#                 },
#                 headers=headers,
#                 timeout=15
#             )

#         try:
#             response = fetch_fastag_bill(access_token)
#             #print(f'{response=}')
#             # 🔁 TOKEN EXPIRED CASE (same as category view)
#             if response.status_code in (401, 403):
#                 if refresh_tokents(request):
#                     new_token = request.session.get("access_token")
#                     response = fetch_fastag_bill(new_token)
#                 else:

#                     return redirect("sign_in")

#             data = response.json()
#             #print(f'{data=}')
#             if response.status_code == 200 and data.get("status"):
#                 # 🔐 STORE IN SESSION
#                 request.session["FASTAG_BILL"] = {
#                     "vehicle_number": vehicle_number,
#                     "billerId": billerId,
#                     "payload": data["data"]["payload"],
#                     "return_payload": data["return_payload"]
#                 }
#                 return redirect("fastag_confirm")

#             else:
#                 messages.error(request, "Unable to fetch FASTag bill")

#         except Exception as e:
#             messages.error(request, f"FASTAG FETCH ERROR: {str(e)}")

#     return render(request, "recharge_fastag/fastag_fetch.html", {
#         "user_data": user_data
#     })




'''
===============================================================================================================
                        Confirm method
===============================================================================================================
'''

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

    return render(request, "recharge_fastag/fastag_confirm.html", context)





# def fastag_payment(request):
#     user_data = request.session.get("user_data", {})
#     access_token = request.session.get("access_token")

#     if not access_token:
#         messages.error(request, "Session expired. Please sign in again.")
#         return redirect("sign_in")

#     bill = request.session.get("FASTAG_BILL", {})

#     if request.method == "POST":
#         amount = request.POST.get("amount")
#         tpin = request.POST.get("tpin")

#         if not amount or not tpin:
#             messages.error(request, "Amount and TPIN are required.")
#             return redirect("fastag_confirm")

#         payload = {
#             "amount": amount,
#             "tpin": tpin,
#             "biller_type": "FASTAG",
#             "return_payload": bill.get("return_payload", {})
#         }

#         def pay_fastag(token):
#             return requests.post(
#                 f"{Baseurl}/recharge-payment/",
#                 json=payload,
#                 headers={
#                     "Authorization": f"Bearer {token}",
#                     "Content-Type": "application/json"
#                 },
#                 timeout=20
#             )

#         # 🔁 Step 1: First API call
#         response = pay_fastag(access_token)
#         #print(f'{response=}')
#         # 🔁 Step 2: Token expired → refresh → retry
#         if response.status_code in (401, 403):
#             if refresh_tokents(request):
#                 new_token = request.session.get("access_token")
#                 response = pay_fastag(new_token)
#             else:
#                 messages.error(request, "Session expired. Please log in again.")
#                 return redirect("sign_in")

#         try:
#             data = response.json()
#             #print(f"{data=}")

#             # ✅ PAYMENT SUCCESS
#             if response.status_code == 200 and data.get("data", {}).get("status") == "SUCCESS":
#                 success_payload = data["data"]["payload"]
#                 #print(f'{success_payload=}')
#                 # 🧹 Clear bill session
#                 request.session.pop("FASTAG_BILL", None)

#                 receipt = {
#                     "customer_name": bill.get("return_payload", {})
#                         .get("customerDetails", {})
#                         .get("EMAIL", ""),
#                     "amount": amount,
#                     "vehicle_number": bill.get("return_payload", {})
#                         .get("customerParams", {})
#                         .get("Vehicle Registration Number", ""),
#                     "transaction_id": success_payload.get("additionalParams", {})
#                         .get("transactionID", ""),
#                     "reference_id": success_payload.get("additionalParams", {})
#                         .get("txnReferenceId", ""),
#                     "approval_ref": success_payload.get("reason", {})
#                         .get("approvalRefNum", ""),
#                     "time": success_payload.get("timeStamp", ""),
#                     "status": data.get("data", {}).get("status"),
#                     "mobile": bill.get("return_payload", {})
#                         .get("customerMobileNumber", ""),
#                     "biller_type": "FASTAG",
#                 }

#                 return render(
#                     request,
#                     "recharge_fastag/fastag_success.html",
#                     {
#                         "message": data.get("message"),
#                         "receipt": receipt,
#                         "user_data": user_data
#                     }
#                 )

#             # ❌ PAYMENT FAILED → show real error
#             error_message = (
#                 data.get("error", {})
#                     .get("payload", {})
#                     .get("errors", [{}])[0]
#                     .get("reason")
#                 or data.get("message")
#                 or "Payment Failed"
#             )

#             # Optional UX cleanup
#             if "already exists" in error_message.lower():
#                 error_message = "Payment already initiated. Please check transaction status."

#             messages.error(request, error_message)

#         except Exception:
#             messages.error(request, "Invalid response from payment server.")

#         return redirect("fastag_confirm")

#     return redirect("fastag_confirm")


'''
===============================================================================================================
                       Payment method
===============================================================================================================
'''
def fastag_payment(request):
    # print('rrrrrrrrrrrr')
    user_data = request.session.get("user_data", {})
    access_token = request.session.get("access_token")
    # biller_type = request.GET.get("biller_type", "Fastag")
    
    if not access_token:
        messages.error(request, "Session expired. Please sign in again.")
        return redirect("sign_in")

    bill = request.session.get("FASTAG_BILL", {})
    # print(f'{bill=}')
    if request.method == "POST":
        amount = request.POST.get("amount")
        tpin = request.POST.get("tpin")
        # print(f'{tpin=}')
      
        payload = {
            "amount": amount,
            'tpin':tpin,
            "biller_type": "Fastag",
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
            print(f'Response: {res}')
            data = res.json()
            print("PAYMENT RESPONSE:", data)

            # ✅ SUCCESS CONDITION
            # if (
            #     res.status_code == 200
            #     and data.get("status") is True
            #     and data.get("data", {}).get("status") == "SUCCESS"
            # ):
            if (
                res.status_code == 200
                and data.get("status") is True
                and data.get("bill_data", {}).get("status") == "SUCCESS"
            ):

                # success_payload = data["data"]["payload"]
                success_payload = data["bill_data"]["payload"]
                # print(f'{success_payload=}')
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

                return render(request, "recharge_fastag/fastag_success.html", {
                    "message": data.get("message"),
                    "receipt": receipt,
                    "user_data": user_data
                })

            # ❌ PAYMENT FAILED
            # return render(request, "recharge_fastag/fastag_confirm.html", {
            #     "vehicle_number": bill.get("vehicle_number", ""),
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
            return redirect("fastag_confirm")


        except requests.RequestException as e:
            #print("REQUEST ERROR:", e)
            return render(request, "recharge_fastag/fastag_confirm.html", {
                "vehicle_number": bill.get("vehicle_number", ""),
                "payload": bill.get("payload", {}),
                "error": "Server error. Please try again.",
                "user_data": user_data
            })
        except Exception as e:
            #print("GENERAL ERROR:", e)
            return render(request, "recharge_fastag/fastag_confirm.html", {
                "vehicle_number": bill.get("vehicle_number", ""),
                "payload": bill.get("payload", {}),
                "error": "Server error. Please try again.",
                "user_data": user_data
            })



