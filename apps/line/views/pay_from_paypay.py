# import environ
# env = environ.Env()
# import paypayopa
# ''' production_mode : Set the connection destination of the sandbox environment / production environment.
# The default false setting connects to the sandbox environment. The True setting connects to the production environment. '''
# API_KEY = env('VUE_APP_API_KEY')
# API_SECRET = env('VUE_APP_API_SECRET')
# client = paypayopa.Client(auth=(API_KEY, API_SECRET), production_mode=False)
# client.set_assume_merchant(env('VUE_APP_MERCHANTID'))

# request = {
#     "merchantPaymentId": "merchant_payment_id",
#     "codeType": "ORDER_QR",
#     "redirectUrl": "http://foobar.com",
#     "redirectType":"WEB_LINK",
#     "orderDescription":"Example - Mune Cake shop",
#     "orderItems": [{
#         "name": "Moon cake",
#         "category": "pasteries",
#         "quantity": 1,
#         "productId": "67678",
#         "unitPrice": {
#             "amount": 1,
#             "currency": "JPY"
#         }
#     }],
#     "amount": {
#         "amount": 1,
#         "currency": "JPY"
#     },
# }
# # Calling the method to create a qr code
# response = client.Code.create_qr_code(request)
# # Printing if the method call was SUCCESS
# print(response['resultInfo']['code'])
