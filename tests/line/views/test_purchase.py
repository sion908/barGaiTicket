from django.test import Client, TestCase
from django.http import Http404
from unittest import mock
from django.utils.timezone import make_aware
from django.urls import reverse

from datetime import datetime
import freezegun
import json
import requests

from apps.core.models import User, Shop, Ticket
from apps.product.models import Product


def create_prod_id(dict):
    class cls():
        def __init__(self, dict) -> None:
            for key, value in dict.items():
                setattr(self, key, value)
    return cls(dict)


def get_user(token):
    user = User.objects.get(lineUserID='lineID')
    return user


def mock_token_get(*args, **kwargs):
    class MockResponse:
        def raise_for_status(self):
            if self.status_code == 200:
                return
            else:
                raise Http404()

        def __init__(self, json_data=None, status_code=200):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'https://api.line.me/v2/profile':
        return MockResponse({'userId': User.objects.first().lineUserID})
    elif args[0].replace('https://api.line.me/oauth2/v2.1/verify?access_token=', '') == 'trueToken':
        return MockResponse()
    else:
        return MockResponse(status_code=400)


class PurchaseTests(TestCase):
    """PurchaseViewのテストクラス"""

    @mock.patch('stripe.Product.create', mock.MagicMock(return_value=create_prod_id({'id': 'prod_123'})))
    @mock.patch('stripe.Price.create', mock.MagicMock(return_value=create_prod_id({'id': 'price_123'})))
    @mock.patch('stripe.checkout.Session.create', mock.MagicMock(return_value=create_prod_id({'url': 'https: //checkout'})))
    def setUp(self):
        self.user = User.objects.create(lineUserID='lineID', is_followed=True)
        self.shopA = Shop.objects.create(name='shopA')
        self.product = Product.objects.create(name='product', price=3000, is_active=True)

    def test_get(self):
        """GET メソッドでアクセスしてステータスコード200を返されることを確認"""

        self.client = Client()

        response = self.client.get(reverse('line:purchase'))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.context_data.get('cant_sell'), None)

    @mock.patch('apps.line.views.lineBase.requests.get', mock.MagicMock(side_effect=mock_token_get))
    @mock.patch('apps.line.views.stripe.checkout.Session.create', mock.MagicMock(return_value=create_prod_id({'url': 'https: //checkout'})))
    def test_get_ticket_limit(self):
        """post 販売チケット数が最大の場合"""

        self.user.create_ticket(
            [{'quantity': 5,
            'kind': self.product,
            'is_pay': True,
            'session_id':"session_id"}]
        )
        self.client = Client()

        response = self.client.get(reverse('line:purchase'))

        self.assertEquals(response.status_code,  200)
        self.assertEquals(response.context_data.get('cant_sell'), True)
        # self.assertEquals(self.user.ticket.first().stub.count(), 1)
        # self.assertEquals(self.user.ticket.count(), 1)

    def test_post_not_csrf(self):
        """csrf認証が含まれていない場合エラー"""
        self.client = Client(enforce_csrf_checks=True)
        response = self.client.post(
            reverse('line:purchase'),
            data={
                str(self.product.pk): 1,
                'lineToken': 'token',
            }
        )
        # If csrf_token was template given.
        # self.assertTemplateUsed(response, 'sample/index.html')
        # If csrf_token was't template given.
        self.assertEquals(response.status_code, 403)

    def test_post_not_linetoken(self):
        """linetokenが含まれていないとエラー"""
        self.client = Client()
        response = self.client.post(reverse('line:purchase'),
                                    data={str(self.product.pk): 1,
                                          })

        self.assertEqual(response.status_code, 404)
        # self.assertRedirects(response, reverse('line:purchase'), status_code=302, target_status_code=200,
        #                      msg_prefix='', fetch_redirect_response=True)

    @mock.patch('apps.line.views.lineBase.requests.get', mock.MagicMock(side_effect=mock_token_get))
    def test_post_faild_token(self):
        """postでtokenが正しくない"""
        self.client = Client()
        response = self.client.post(
            reverse('line:purchase'),
            data={
                str(self.product.pk): '1',
                'lineToken': 'badToken',
            }
        )

        self.assertEqual(response.status_code, 404)
        # self.assertRedirects(response, reverse('line:purchase'), status_code=404, target_status_code=200,
        #                      msg_prefix='', fetch_redirect_response=True)

    @mock.patch('apps.line.views.lineBase.requests.get', mock.MagicMock(side_effect=mock_token_get))
    @mock.patch('apps.line.views.stripe.checkout.Session.create', mock.MagicMock(return_value=create_prod_id({'url': 'https: //checkout'})))
    def test_post(self):
        """正しくpost"""
        self.client = Client()
        response = self.client.post(
            reverse('line:purchase'),
            data={
                str(self.product.pk): '1',
                'lineToken': 'trueToken',
            }
        )
        # import pdb
        # pdb.set_trace()
        self.assertEquals(response.status_code, 302)
        # self.assertEquals(response.json(), {'success': 'ok'})
        # self.assertEquals(self.user.ticket.first().stub.count(), 1)
        # self.assertEquals(self.user.ticket.count(), 1)


class purchase_successTests(TestCase):
    """purchase_successのAPI テストクラス"""

    def create_prod_id(dict):
        class cls():
            def __init__(self, dict) -> None:
                for key, value in dict.items():
                    setattr(self, key, value)
        return cls(dict)

    def get_user(token):
        user = User.objects.get(lineUserID='lineID')
        return user

    def mock_token_get(url, headers=None):
        class cls():
            def __init__(self, dict) -> None:
                for key, value in dict.items():
                    setattr(self, key, value)
        if headers:
            return cls({'userId': User.objects.fistst().pk})
        token = url.replace('https: //api.line.me/oauth2/v2.1/verify?access_token=', '')
        if token == "trueToken":
            return cls({'status_code': 200})
        else:
            return cls({'status_code': 400})

    def readJson(filename):
        path = 'tests/line/data/' + filename + '.json'
        json_open = open(path, 'r')
        json_load = json.load(json_open)
        return json_load

    # 検証用のDjangoへの通知をテスト時にはそれとわかるように出したかった
    # def testPostDjango(*args, **kwargs):
    #     print(args,kwargs)
    #     args[1] = "test\n" + args[1]
    #     requests.post(*args, **kwargs)

    @mock.patch('stripe.Product.create', mock.MagicMock(return_value=create_prod_id({'id': 'prod_123'})))
    @mock.patch('stripe.Price.create', mock.MagicMock(return_value=create_prod_id({'id': 'price_1LFaA5IkZUNdggLMSXgomDvW'})))
    # @mock.patch('apps.line.views.views_purchase.requests.post', mock.MagicMock(side_effect=testPostDjango))
    # @mock.patch('apps.line.views.views_purchase.requests.get', mock.MagicMock(side_effect=mock_token_get))
    def setUp(self):
        self.user = User.objects.create(lineUserID='lineID', is_followed=True)
        self.shopA = Shop.objects.create(name='shopA')
        self.product = Product.objects.create(
            name='product',
            price=3000,
            price_id='price_1LFaA5IkZUNdggLMSXgomDvW',
            sale_dt=make_aware(datetime(2022, 9, 1)),
            start_dt=make_aware(datetime(2022, 9, 11)),
            end_dt=make_aware(datetime(2022, 9, 13))
        )
        self.freezer = freezegun.freeze_time('2022-9-3')
        self.freezer.start()

    def tearDown(self):
        self.freezer.stop()

    def test_get_not_sessionID(self):
        """sessionIDなしでGET メソッドでアクセスしてステータスコード404を返されることを確認"""

        self.client = Client()

        response = self.client.get(reverse('line:purchase_suc'))
        self.assertEqual(response.status_code, 404)

    @mock.patch('stripe.checkout.Session.retrieve', mock.MagicMock(return_value=readJson('checkout_retrive')))
    def test_post(self):
        """正しくget"""
        self.client = Client()
        response = self.client.get(reverse('line:purchase_suc') + '?session_id=session_id')

        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.user.ticket.all().count(), 1)
        ticket = self.user.ticket.first()
        self.assertEquals(ticket.situation, Ticket.SITUATION_BEFORE)

    @mock.patch('stripe.checkout.Session.retrieve', mock.MagicMock(return_value=readJson('checkout_retrive')))
    @mock.patch('apps.line.views.lineBase.line_bot_api.link_rich_menu_to_user', mock.MagicMock(return_value=''))
    @freezegun.freeze_time('2022-9-11 12:34:56')
    def test_post_betweent_time(self):
        """販売期間内に購入get"""
        self.client = Client()
        response = self.client.get(reverse('line:purchase_suc') + '?session_id=session_id')

        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.user.ticket.all().count(), 1)
        ticket = self.user.ticket.first()
        self.assertEquals(ticket.situation, Ticket.SITUATION_USABLE)

    @mock.patch('stripe.checkout.Session.retrieve', mock.MagicMock(return_value=readJson('checkout_retrive')))
    @freezegun.freeze_time('2022-9-20 12:34:56')
    def test_post_aft_time(self):
        """利用期間内にget"""
        self.client = Client()
        response = self.client.get(reverse('line:purchase_suc') + '?session_id=session_id')

        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.user.ticket.all().count(), 1)
        ticket = self.user.ticket.first()
        self.assertEquals(ticket.situation, Ticket.SITUATION_BEFORE)
