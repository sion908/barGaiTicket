from django.shortcuts import redirect
from django.test import Client, TestCase
from django.urls import reverse
from unittest import mock

from apps.core.models import User, Shop, Ticket
from apps.core.models import Product
from tests.setup.product_setup import create_prod_id

import requests

# requests lib の mock 関数内関数?にしてsideeffectに渡したかった
def mocked_requests_get(**orig_kwargs):
    def func(*args, **kwargs):
        class MockResponse(requests.Response):
            def __init__(self, json_data, status_code):
                super().__init__()
                self.json_data = json_data
                self.status_code = status_code
            def json(self):
                return self.json_data
        print(args,kwargs)
        if orig_kwargs.get("notoken"):
            return MockResponse({}, 404)
        elif orig_kwargs.get("invalid"):
            if "verify" in args[0]:
                return MockResponse({}, 404)
        elif orig_kwargs.get("noPermission"):
            if "profile" in args[0]:
                return MockResponse({}, 404)
        return MockResponse({"userId": orig_kwargs.get("userId", "lineID")}, 200)
    return func


class shopTests(TestCase):
    """getShop_and_numのテストクラス"""

    @mock.patch('stripe.Product.create', mock.MagicMock(return_value=create_prod_id(id='prod_123')))
    @mock.patch('stripe.Price.create', mock.MagicMock(return_value=create_prod_id(id='price_123')))
    def setUp(self):
        self.user = User.objects.create(lineUserID='lineID')
        self.shop = Shop.objects.create(name="shopA")
        self.product = Product.objects.create(name='product', price=3000, is_active=True)
        self.ticket = Ticket.objects.create(owner=self.user, kind=self.product, situation=Ticket.SITUATION_USABLE)

    @mock.patch('apps.line.views.lineBase.requests.get', mock.MagicMock(side_effect=mocked_requests_get(notoken=1)))
    def test_no_token(self):
        """GET メソッドでアクセスしてtokenがおかしい場合"""

        self.client = Client()

        # with self.assertRaises(ValueError):
        response = self.client.get(reverse('api:shop',
                                   kwargs={'token': "failed", 'shopID': self.shop.pk}))

        self.assertEqual(response.status_code, 404)

    @mock.patch('apps.line.views.lineBase.requests.get', mock.MagicMock(side_effect=mocked_requests_get(invalid=1)))
    def test_invalid_token(self):
        """GET メソッドでアクセスしてtokenがおかしい場合"""

        self.client = Client()

        # with self.assertRaises(ValueError):
        response = self.client.get(reverse('api:shop',
                                   kwargs={'token': "failed", 'shopID': self.shop.pk}))

        self.assertEqual(response.status_code, 404)

    @mock.patch('apps.line.views.lineBase.requests.get', mock.MagicMock(side_effect=mocked_requests_get(noPermission=1)))
    def test_noPermission(self):
        """GET メソッドでアクセスしてtokenがおかしい場合"""

        self.client = Client()

        # with self.assertRaises(ValueError):
        response = self.client.get(reverse('api:shop',
                                   kwargs={'token': "failed", 'shopID': self.shop.pk}))

        self.assertEqual(response.status_code, 404)

    @mock.patch('apps.line.views.lineBase.requests.get', mock.MagicMock(side_effect=mocked_requests_get()))
    def test_get(self):
        """GET メソッドでアクセスしてステータスコード200を返されることを確認"""

        self.client = Client()

        response = self.client.get(reverse('api:shop',
                                   kwargs={'token': '1', 'shopID': self.shop.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user': {'maxuse': 3, 'used': 0}, 'shop': {'name': self.shop.name}})

    @mock.patch('apps.line.views.lineBase.requests.get', mock.MagicMock(side_effect=mocked_requests_get()))
    def test_get_with_ticket(self):
        """GET メソッドでアクセス
        一店舗で使ってたら使える枚数が２マイ，使用済みが一枚
        """

        self.user.ticket.use_by_count(self.shop, 1, self.product)

        self.client = Client()

        response = self.client.get(reverse('api:shop',
                                   kwargs={'token': '1', 'shopID': self.shop.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user': {'maxuse': 2, 'used': 1}, 'shop': {'name': self.shop.name}})

    @mock.patch('apps.line.views.lineBase.requests.get', mock.MagicMock(side_effect=mocked_requests_get()))
    def test_get_with_tickets(self):
        """GET メソッドでアクセス
        所持tiketが二枚
        一店舗で3枚使ってたら使える枚数が3マイ, 使用済みが3枚
        """

        self.ticket = Ticket.objects.create(owner=self.user, kind=self.product, situation=Ticket.SITUATION_USABLE)

        self.user.ticket.use_by_count(self.shop, 3, self.product)

        self.client = Client()

        response = self.client.get(reverse('api:shop',
                                   kwargs={'token': '1', 'shopID': self.shop.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user': {'maxuse': 3, 'used': 3}, 'shop': {'name': self.shop.name}})

    @mock.patch('apps.line.views.lineBase.requests.get', mock.MagicMock(side_effect=mocked_requests_get()))
    def test_get_with_not_active(self):
        """GET メソッドでアクセス
        非activeなtiket一枚
        一店舗で一枚も使えない
        """

        self.ticket.situation = Ticket.SITUATION_BEFORE
        self.ticket.save()

        self.client = Client()

        response = self.client.get(reverse('api:shop',
                                   kwargs={'token': '1', 'shopID': self.shop.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'user': {'maxuse': 0, 'used': 0}, 'shop': {'name': self.shop.name}})

    @mock.patch('apps.line.views.lineBase.requests.get', mock.MagicMock(side_effect=mocked_requests_get(**{"userId":"failedID"})))
    def test_get_with_not_account(self):
        """GET メソッドでアクセス
        非activeなtiket一枚
        一店舗で一枚も使えない
        """

        self.client = Client()

        response = self.client.get(reverse('api:shop',
                                   kwargs={'token': '1k', 'shopID': self.shop.pk}))

        self.assertEqual(response.status_code, 200)

        # self.assertRedirects(response, redirect('line:purchase'), status_code=302, target_status_code=200)
        self.assertEqual(response.json(), {"url": reverse('line:purchase')})

