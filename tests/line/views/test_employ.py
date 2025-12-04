from django.test import Client, TestCase
from apps.product.models import Product
from unittest import mock
from django.urls import reverse

from apps.core.models import User, Shop, Ticket


class EmployTests(TestCase):
    """EmployViewのテストクラス"""
    def create_prod_id(id):
        class Prod_class():
            id = ""

            def __init__(self, pro):
                self.id = pro
        return Prod_class(id)

    def get_user(token):
        user = User.objects.get(lineUserID='lineID')
        return user, True

    @mock.patch('stripe.Product.create', mock.MagicMock(return_value=create_prod_id(id='prod_123')))
    @mock.patch('stripe.Price.create', mock.MagicMock(return_value=create_prod_id(id='price_123')))
    def setUp(self):
        self.user = User.objects.create(lineUserID='lineID', is_followed=True)
        self.shopA = Shop.objects.create(name='shopA')
        self.product = Product.objects.create(name='product', price=3000, is_active=True)

    def test_get(self):
        """GET メソッドでアクセスしてステータスコード200を返されることを確認"""

        self.client = Client()

        response = self.client.get(reverse('line:employ'))
        self.assertEqual(response.status_code, 200)

    @mock.patch('apps.line.views.views_employ.get_lineuser_by_token', mock.MagicMock(side_effect=get_user))
    def test_post_not_csrf(self):
        """csrf認証が含まれていない場合エラー"""
        self.client = Client(enforce_csrf_checks=True)
        response = self.client.post(
            reverse('line:employ'),
            data={
                'shop_id': self.shopA.pk,
                'lineToken': 'token',
                'employ_num': 1,
            }
        )
        # If csrf_token was template given.
        # self.assertTemplateUsed(response, 'sample/index.html')
        # If csrf_token was't template given.
        self.assertEquals(response.status_code, 403)

    @mock.patch('apps.line.views.views_employ.get_lineuser_by_token', mock.MagicMock(side_effect=get_user))
    def test_post(self):
        self.ticket = Ticket.objects.create(owner=self.user, kind=self.product, situation=Ticket.SITUATION_USABLE)
        self.client = Client()
        response = self.client.post(
            reverse('line:employ'),
            data={
                'shop_id': self.shopA.pk,
                'lineToken': 'token',
                'employ_num': 1,
            }
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json(), {'success': 'ok'})
        self.assertEquals(self.user.ticket.first().stub.count(), 1)
        self.assertEquals(self.user.ticket.count(), 1)

    @mock.patch('apps.line.views.views_employ.get_lineuser_by_token', mock.MagicMock(side_effect=get_user))
    def test_post_have_two(self):
        self.ticket0 = Ticket.objects.create(owner=self.user, kind=self.product, situation=Ticket.SITUATION_USABLE)
        self.ticket1 = Ticket.objects.create(owner=self.user, kind=self.product, situation=Ticket.SITUATION_USABLE)
        self.client = Client()
        response = self.client.post(
            reverse('line:employ'),
            data={
                'shop_id': self.shopA.pk,
                'lineToken': 'token',
                'employ_num': 3,
            }
        )
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json(), {'success': 'ok'})
        self.assertEquals(self.user.ticket.count(), 2)
        self.assertEquals(self.ticket0.stub.count(), 2)
        self.assertEquals(self.ticket1.stub.count(), 1)
        self.assertEquals(self.ticket1.stub.first().shop, self.shopA)
