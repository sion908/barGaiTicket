# from django.test import TestCase
# from django.urls import reverse, resolve
# from apps.core.views import HomeView, BuyView, purchase_confirmation, EmployView, employ_confirmation, employ_approve
# from ..setup import initial_user, initial_shop, create_user_ticket

# urlpatterns = [
#         path('', HomeView.as_view(), name='home'),
#         path('purchase/', BuyView.as_view(), name='buy'),
#         path('purchase/complete', purchase_confirmation, name='buy_comp'),
#         path('employ/', EmployView.as_view(), name='employ'),
#         path('employ/procedure', employ_confirmation, name='employ_procedure'),
#         path('employ/approve/<int:employ_num>/<uuid:pk>/', employ_approve, name='employ_approve'),
# ]


# class TestUrls(TestCase):
#     """core ページへのURLでアクセスする時のリダイレクトをテスト"""

#     def test_home_url(self):
#         view = resolve(reverse('app:home'))
#         self.assertEqual(view.func.view_class, HomeView)

# def test_buy_url(self):
#     view = resolve(reverse('app:buy'))
#     self.assertEqual(view.func.view_class, BuyView)

# def test_buy_comp_url(self):
#     view = resolve(reverse('app:buy_comp'))
#     self.assertEqual(view.func, purchase_confirmation)

# def test_employ_url(self):
#     view = resolve(reverse('app:employ'))
#     self.assertEqual(view.func.view_class, EmployView)

# def test_employ_procedure_url(self):
#     view = resolve(reverse('app:employ_procedure'))
#     self.assertEqual(view.func, employ_confirmation)

# def test_employ_approve_url(self):
#     initial_shop(self,2)
#     create_user_ticket(self)
#     view = resolve(reverse('app:employ_approve', kwargs={'pk':str(self.shops[0].pk),'employ_num':'1'}))
#     self.assertEqual(view.func, employ_approve)

#     def test_get_update_url(self):
#         view = resolve(reverse('product:update'))
#         self.assertEqual(view.func, update_products)
