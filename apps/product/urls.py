from django.urls import path

from . import views

app_name = 'product'

urlpatterns = [
    # path('create', views.create_product, name='create'),
    # path('show', views.show_products, name='show'),
    # path('update', views.update_products, name='update'),
    path('showShop', views.show_shops, name='showShop'),
]
