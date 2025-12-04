from django.test import Client, TestCase, RequestFactory
from django.urls import reverse
from django.utils.timezone import make_aware
from unittest import mock
import freezegun

from apps.core.models import User, Shop, Ticket, Owner, Stub
from apps.core.models import Product
from tests.setup.product_setup import create_prod_id
from api.views import getNotificationOfSuccessPayment

import requests
from datetime import datetime

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
        self.assertEqual(rej['stubs'][0]['time'], stubs.first().updated_at.isoformat(timespec='microseconds').split('+')[0] + 'Z')

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
        self.assertEqual(rej['stubs'][0]['time'], stubs.first().updated_at.isoformat(timespec='microseconds').split('+')[0] + 'Z')

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


class stubLTests(TestCase):
    """getStubsWithLoginのテストクラス"""

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
    def test_get_with_not_login(self):
        """ログインなしでGETメソッドでアクセスしてステータスコード302を返されることを確認
           ログイン画面へ"""

        self.client = Client()

        response = self.client.get(reverse('api:stubL'))

        self.assertEqual(response.status_code, 302)

    def test_get(self):
        """GET メソッドでアクセスしてステータスコード200を返されることを確認"""

        self.client = Client()
        self.client.force_login(self.owner)

        response = self.client.get(reverse('api:stubL'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'shop': 'shopA', 'stubs': []})

    def test_get_with_ticket(self):
        """GET メソッドでアクセス
        stubがいっこ
        """

        self.user.ticket.use_by_count(self.shop, 1, self.product)
        self.client = Client()
        self.client.force_login(self.owner)

        response = self.client.get(reverse('api:stubL'))

        stubs = Stub.objects.filter(shop=self.shop, is_used=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(stubs.count(), 1)

        rej = response.json()
        self.assertEqual(rej['shop'], 'shopA')
        self.assertEqual(len(rej['stubs']), stubs.count())
        self.assertEqual(rej['stubs'][0]['pk'], stubs.first().pk)
        self.assertEqual(rej['stubs'][0]['user_id'], stubs.first().ticket.owner.pk)
        self.assertEqual(rej['stubs'][0]['time'], stubs.first().updated_at.isoformat(timespec='microseconds').split('+')[0] + 'Z')

    def test_get_with_anotherShop(self):
        """GET メソッドでアクセス
        stubがいっこ
        """

        self.user.ticket.use_by_count(self.shop, 1, self.product)
        self.client = Client()
        self.client.force_login(self.owner)
        self.shopb = Shop.objects.create(name="shopB")
        self.user.ticket.use_by_count(self.shopb, 1, self.product)

        response = self.client.get(reverse('api:stubL'))

        stubs = Stub.objects.filter(shop=self.shop, is_used=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(stubs.count(), 1)

        rej = response.json()
        self.assertEqual(rej['shop'], 'shopA')
        self.assertEqual(len(rej['stubs']), stubs.count())
        self.assertEqual(rej['stubs'][0]['pk'], stubs.first().pk)
        self.assertEqual(rej['stubs'][0]['user_id'], stubs.first().ticket.owner.pk)
        self.assertEqual(rej['stubs'][0]['time'], stubs.first().updated_at.isoformat(timespec='microseconds').split('+')[0] + 'Z')

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
        self.client.force_login(self.owner)

        response = self.client.get(reverse('api:stubL'))

        stubs = Stub.objects.filter(shop=self.shop, is_used=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(stubs.count(), 5)
        rej = response.json()
        self.assertEqual(rej['shop'], 'shopA')
        self.assertEqual(len(rej['stubs']), stubs.count())


class paidTests(TestCase):
    """getNotificationOfSuccessPaymentのテストクラス"""
    session_id = "se_id"
    def get_event(**kwargs):
        event = {
            'type': kwargs.get('type','checkout.session.completed'),
            'data': {
                'object': {
                    "id": "se_id",
                    "amount_subtotal": kwargs.get("amount_subtotal",3000),
                    "metadata": {
                        "user_id": kwargs.get("user_id",'lineID')
                    },
                }
            }
        }
        return event

    @mock.patch('stripe.Product.create', mock.MagicMock(return_value=create_prod_id(id='prod_123')))
    @mock.patch('stripe.Price.create', mock.MagicMock(return_value=create_prod_id(id='price_123')))
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create(lineUserID='lineID')
        self.product = Product.objects.create(
            name='product',
            price=3000,
            is_active=True,
            sale_dt=make_aware(datetime(2022, 9, 1)),
            start_dt=make_aware(datetime(2022, 9, 11)),
            end_dt=make_aware(datetime(2022, 9, 13))
        )

    @mock.patch('stripe.Webhook.construct_event', mock.MagicMock(return_value=get_event()))
    def test_get(self):
        """getメソッドでアクセスしてエラー"""

        # Create an instance of a GET request.
        request = self.factory.get(reverse('api:paid'))

        # Recall that middleware are not supported. You can simulate a
        # logged-in user by setting request.user manually.
        request.data = "payload"

        # Or you can simulate an anonymous user by setting request.user to
        # an AnonymousUser instance.
        request.headers = {
            'STRIPE_SIGNATURE': "sig_header"
        }

        # Test my_view() as if it were deployed at /customer/details
        response = getNotificationOfSuccessPayment(request)

        # self.client = Client()

        # response = self.client.get(reverse('api:paid'))

        self.assertEqual(response.status_code, 405)

    @mock.patch('stripe.Webhook.construct_event', mock.MagicMock(return_value=get_event()))
    def test_post_no_ticket(self):
        """postメソッドでアクセス,チケットを持っていない場合，処理後一個持ってる"""

        # Create an instance of a GET request.
        request = self.factory.post(reverse('api:paid'))

        # Recall that middleware are not supported. You can simulate a
        # logged-in user by setting request.user manually.
        request.data = "payload"

        # Or you can simulate an anonymous user by setting request.user to
        # an AnonymousUser instance.
        request.headers = {
            'STRIPE_SIGNATURE': "sig_header"
        }

        # Test my_view() as if it were deployed at /customer/details
        response = getNotificationOfSuccessPayment(request)

        # self.client = Client()

        # response = self.client.get(reverse('api:paid'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.ticket.all().count(), 1)

    @mock.patch('stripe.Webhook.construct_event', mock.MagicMock(return_value=get_event()))
    def test_post_had_one_Ticket(self):
        """postメソッドでアクセス,処理済み場合，変化はない"""
        
        self.user.create_ticket([{
                'quantity': 1,
                'kind': self.product,
                'is_pay': True,
                'session_id': self.session_id
            }])

        # Create an instance of a GET request.
        request = self.factory.post(reverse('api:paid'))

        # Recall that middleware are not supported. You can simulate a
        # logged-in user by setting request.user manually.
        request.data = "payload"

        # Or you can simulate an anonymous user by setting request.user to
        # an AnonymousUser instance.
        request.headers = {
            'STRIPE_SIGNATURE': "sig_header"
        }

        # Test my_view() as if it were deployed at /customer/details
        response = getNotificationOfSuccessPayment(request)

        # self.client = Client()

        # response = self.client.get(reverse('api:paid'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.ticket.all().count(), 1)

