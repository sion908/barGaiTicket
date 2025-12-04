from django.urls import path
from .views import (
    index, trans,
    PurchaseView, EmployView,
    purchase_success, purchase_cansel, showDashboad)

app_name = 'line'

urlpatterns = [
    path('', index, name='callback'),
    path('trans/', trans, name='trans'),
    path('trans/purchase/', PurchaseView.as_view(), name='purchase'),
    path('trans/purchase/success', purchase_success, name='purchase_suc'),
    path('trans/purchase/cansel', purchase_cansel, name='purchase_can'),
    path('trans/employ/', EmployView.as_view(), name='employ'),
    path('dashboard', showDashboad, name='dashboard'),
]
