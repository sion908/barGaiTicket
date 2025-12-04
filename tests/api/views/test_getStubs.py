from django.test import Client, TestCase
from django.urls import reverse
from unittest import mock

from apps.core.models import User, Shop, Ticket, Owner, Stub
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
        return MockResponse({"userId": "lineID"}, 200)
    return func


class getStubTests(TestCase):
    """getStubsのテストクラス"""

    @mock.patch('stripe.Product.create', mock.MagicMock(return_value=create_prod_id(id='prod_123')))
    @mock.patch('stripe.Price.create', mock.MagicMock(return_value=create_prod_id(id='price_123')))
    def setUp(self):
        self.user = User.objects.create(lineUserID='lineID')
        self.owner = Owner.objects.create_user('uni', 'wa@yahoo.co.jp', "uni", user=self.user)
        self.shop = Shop.objects.create(name="shopA")
        self.product = Product.objects.create(name='product', price=3000, is_active=True)
        self.ticket = Ticket.objects.create(owner=self.user, kind=self.product, situation=Ticket.SITUATION_USABLE)
        self.ticket = Ticket.objects.create(owner=self.user, kind=self.product, situation=Ticket.SITUATION_USABLE)
        self.owner.shop = self.shop
        self.owner.save()
        boughts = [
            {
                'quantity': 1,
                'kind': self.product,
                'is_pay': True,
                'session_id': 'session_id',
                'situation': Ticket.SITUATION_USABLE
            },
        ]
        self.user.create_ticket(boughts)

    @mock.patch('apps.line.views.lineBase.requests.get', mock.MagicMock(side_effect=mocked_requests_get()))
    def test_get(self):
        """GET メソッドでアクセスしてステータスコード200を返されることを確認"""

        self.client = Client()

        response = self.client.get(reverse('api:stub', kwargs={'token': '1'}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'shop': 'shopA', 'stubs': []})

    @mock.patch('apps.line.views.lineBase.requests.get', mock.MagicMock(side_effect=mocked_requests_get()))
    def test_get_with_ticket(self):
        """GET メソッドでアクセス
        stubがいっこ
        """

        self.user.ticket.use_by_count(self.shop, 1, self.product)
        self.client = Client()

        response = self.client.get(reverse('api:stub', kwargs={'token': '1'}))

        stubs = Stub.objects.filter(shop=self.shop, is_used=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(stubs.count(), 1)

        rej = response.json()
        self.assertEqual(rej['shop'], 'shopA')
        self.assertEqual(len(rej['stubs']), stubs.count())
        self.assertEqual(rej['stubs'][0]['pk'], stubs.first().pk)
        self.assertEqual(rej['stubs'][0]['user_id'], stubs.first().ticket.owner.pk)
        self.assertEqual(rej['stubs'][0]['time'], stubs.first().updated_at.isoformat(timespec='seconds').split('+')[0] + 'Z')

    @mock.patch('apps.line.views.lineBase.requests.get', mock.MagicMock(side_effect=mocked_requests_get()))
    def test_get_with_anotherShop(self):
        """GET メソッドでアクセス
        stubがいっこ
        """

        self.user.ticket.use_by_count(self.shop, 1, self.product)
        self.client = Client()
        self.shopb = Shop.objects.create(name="shopB")
        self.user.ticket.use_by_count(self.shopb, 1, self.product)

        response = self.client.get(reverse('api:stub', kwargs={'token': '1'}))

        stubs = Stub.objects.filter(shop=self.shop, is_used=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(stubs.count(), 1)

        rej = response.json()
        self.assertEqual(rej['shop'], 'shopA')
        self.assertEqual(len(rej['stubs']), stubs.count())
        self.assertEqual(rej['stubs'][0]['pk'], stubs.first().pk)
        self.assertEqual(rej['stubs'][0]['user_id'], stubs.first().ticket.owner.pk)
        self.assertEqual(rej['stubs'][0]['time'], stubs.first().updated_at.isoformat(timespec='seconds').split('+')[0] + 'Z')

    @mock.patch('apps.line.views.lineBase.requests.get', mock.MagicMock(side_effect=mocked_requests_get()))
    def test_get_with_two_person(self):
        """GET メソッドでアクセス
        stubがいっこ
        """

        self.user1 = User.objects.create(lineUserID='line1ID')
        boughts = [
            {
                'quantity': 2,
                'kind': self.product,
                'is_pay': True,
                'session_id': 'session_id',
                'situation': Ticket.SITUATION_USABLE
            },
        ]
        self.user1.create_ticket(boughts)

        self.user.ticket.use_by_count(self.shop, 1, self.product)
        self.user1.ticket.use_by_count(self.shop, 4, self.product)
        self.client = Client()

        response = self.client.get(reverse('api:stub', kwargs={'token': '1'}))

        stubs = Stub.objects.filter(shop=self.shop, is_used=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(stubs.count(), 5)
        rej = response.json()
        self.assertEqual(rej['shop'], 'shopA')
        self.assertEqual(len(rej['stubs']), stubs.count())

