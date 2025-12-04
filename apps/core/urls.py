from django.urls import path

from .views import HomeView, HomeDetailView  # , BuyView, purchase_confirmation, EmployView, employ_confirmation, employ_approve

app_name = 'app'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('detail', HomeDetailView.as_view(), name='detail'),
    # path('purchase/', BuyView.as_view(), name='buy'),
    # path('purchase/complete', purchase_confirmation, name='buy_comp'),
    # path('employ/', EmployView.as_view(), name='employ'),
    # path('employ/procedure', employ_confirmation, name='employ_procedure'),
    # path('employ/approve/<int:employ_num>/<uuid:pk>/', employ_approve, name='employ_approve'),
]
