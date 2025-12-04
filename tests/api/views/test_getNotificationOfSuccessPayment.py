from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.utils.timezone import make_aware
from unittest import mock
import freezegun

from apps.core.models import User, Ticket
from apps.core.models import Product
from tests.setup.product_setup import create_prod_id
from api.views import getNotificationOfSuccessPayment

from datetime import datetime


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
            sale_dt=make_aware(datetime(2022, 9, 2)),
            start_dt=make_aware(datetime(2022, 9, 11)),
            end_dt=make_aware(datetime(2022, 9, 13))
        )
        self.freezer = freezegun.freeze_time('2022-9-1')
        self.freezer.start()



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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.ticket.all().count(), 1)
        self.assertEqual(self.user.ticket.first().situation, Ticket.SITUATION_BEFORE)

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

    @mock.patch('stripe.Webhook.construct_event', mock.MagicMock(return_value=get_event()))
    @freezegun.freeze_time('2022-9-12 12:34:56')
    def test_post_intime(self):
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

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.user.ticket.all().count(), 1)
        self.assertEqual(self.user.ticket.first().situation, Ticket.SITUATION_USABLE)
