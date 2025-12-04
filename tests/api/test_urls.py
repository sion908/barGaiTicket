from django.test import TestCase
from django.urls import reverse, resolve

from api.views import getShop_and_num, getStubs, getNotificationOfSuccessPayment


class TestUrls(TestCase):
    """core ページへのURLでアクセスする時のリダイレクトをテスト"""

    def test_shop_url(self):
        view = resolve(reverse('api:shop', kwargs={'token': '1', 'shopID': 'fbf2160a-1b28-4398-9204-f1c01ccdd931'}))
        self.assertEqual(view.func, getShop_and_num)

    def test_stub_url(self):
        view = resolve(reverse('api:stub', kwargs={'token': '1'}))
        self.assertEqual(view.func, getStubs)

    def test_stub_url(self):
        view = resolve(reverse('api:paid'))
        self.assertEqual(view.func, getNotificationOfSuccessPayment)
