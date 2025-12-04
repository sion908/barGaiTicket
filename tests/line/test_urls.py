from django.test import TestCase
from django.urls import reverse, resolve
from apps.line.views import (
    index, trans,
    PurchaseView, EmployView,
    purchase_success, purchase_cansel)


class TestUrls(TestCase):
    """index ページへのURLでアクセスする時のリダイレクトをテスト"""

    def test_get_callback(self):
        view = resolve(reverse('line:callback'))
        self.assertEqual(view.func, index)

    def test_get_trans(self):
        view = resolve(reverse('line:trans'))
        self.assertEqual(view.func, trans)

    def test_get_purchase(self):
        view = resolve(reverse('line:purchase'))
        self.assertEqual(view.func.view_class, PurchaseView)

    def test_get_purchase_suc(self):
        view = resolve(reverse('line:purchase_suc'))
        self.assertEqual(view.func, purchase_success)

    def test_get_purchase_can(self):
        view = resolve(reverse('line:purchase_can'))
        self.assertEqual(view.func, purchase_cansel)

    def test_get_employ(self):
        view = resolve(reverse('line:employ'))
        self.assertEqual(view.func.view_class, EmployView)
