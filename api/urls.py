# coding: utf-8
from django.urls import path  # , include

# from rest_framework import routers
from .views import (
    getShop_and_num,
    getStubs,
    getStubsWithLogin,
    getNotificationOfSuccessPayment
)

app_name = 'api'

# router = routers.DefaultRouter()
# # router.register(r'users', UserTicketViewSet)
# router.register(r'shop', ShopViewSet)

urlpatterns = [
    # path("", include(router.urls)),
    path('shop/<str:token>/<uuid:shopID>/', getShop_and_num, name='shop'),
    path('stub/<str:token>/', getStubs, name='stub'),
    path('stub/', getStubsWithLogin, name='stubL'),
    path('paid', getNotificationOfSuccessPayment, name='paid'),
]
