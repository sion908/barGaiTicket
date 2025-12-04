from django.test import TestCase
from apps.core.models import Shop, Ticket, Stub
from apps.product.models import Product
from unittest import mock

from ..setup import initial_user


class TicketModelTest(TestCase):

    def create_prod_id(id):
        class Prod_class():
            id = ""

            def __init__(self, pro):
                self.id = pro
        return Prod_class(id)

    @mock.patch('stripe.Product.create', mock.MagicMock(return_value=create_prod_id(id='prod_123')))
    @mock.patch('stripe.Price.create', mock.MagicMock(return_value=create_prod_id(id='price_123')))
    def setUp(self):
        initial_user(self)
        self.shopA = Shop.objects.create(name='shopA')
        self.product = Product.objects.create(name='product', price=3000)

    def test_is_empty(self):
        """初期状態では何も登録されていないことをチェック"""
        saved_tickets = Ticket.objects.all()
        self.assertEqual(saved_tickets.count(), 0)

    def test_is_count_one(self):
        """1つレコードを適当に作成すると、レコードが1つだけカウントされることをテスト"""
        ticket = Ticket(owner=self.user, kind=self.product)
        ticket.save()
        saved_tickets = Ticket.objects.all()
        self.assertEqual(saved_tickets.count(), 1)

    def test_saving_and_retrieving_user(self):
        """内容を指定してデータを保存し、すぐに取り出した時に保存した時と同じ値が返されることをテスト"""

        Ticket.objects.create(
            owner=self.user,
            kind=self.product,
        )

        actual_ticket = Ticket.objects.first()

        self.assertEqual(actual_ticket.owner, self.user, 'チケットの持ち主が正しい')
        self.assertEqual(actual_ticket.kind, self.product, 'チケットの種別が正しい')
        self.assertFalse(actual_ticket.is_pay, "支払いが行われていない")


class StubModelTest(TestCase):

    def create_prod_id(id):
        class Prod_class():
            id = ""

            def __init__(self, pro):
                self.id = pro
        return Prod_class(id)

    @mock.patch('stripe.Product.create', mock.MagicMock(return_value=create_prod_id(id='prod_123')))
    @mock.patch('stripe.Price.create', mock.MagicMock(return_value=create_prod_id(id='price_123')))
    def setUp(self):
        initial_user(self)
        self.shopA = Shop.objects.create(name='shopA')
        self.shopB = Shop.objects.create(name='shopB')
        self.shopC = Shop.objects.create(name='shopC')
        self.product = Product.objects.create(name='product', price=3000)
        self.ticket = Ticket.objects.create(
            owner=self.user,
            kind=self.product,
        )

    def test_is_empty(self):
        """初期状態では何も登録されていないことをチェック"""
        saved_tickets = Stub.objects.all()
        self.assertEqual(saved_tickets.count(), 0)

    def test_is_count_one(self):
        """1つレコードを適当に作成すると、レコードが1つだけカウントされることをテスト"""
        stub = Stub(ticket=self.ticket, shop=self.shopA)
        stub.save()
        saved_stubs = Stub.objects.all()
        self.assertEqual(saved_stubs.count(), 1)

    def test_saving_and_retrieving_user(self):
        """内容を指定してデータを保存し、すぐに取り出した時に保存した時と同じ値が返されることをテスト"""

        Stub.objects.create(
            ticket=self.ticket,
            shop=self.shopA,
        )

        actual_stub = Stub.objects.first()

        self.assertEqual(actual_stub.ticket, self.ticket, 'チケットの持ち主が正しい')
        self.assertEqual(actual_stub.shop, self.shopA, 'チケットの種別が正しい')
        self.assertFalse(actual_stub.is_used, "支払いが行われていない")


class UseTicketTest(TestCase):

    def create_prod_id(id):
        class Prod_class():
            id = ""

            def __init__(self, pro):
                self.id = pro
        return Prod_class(id)

    @mock.patch('stripe.Product.create', mock.MagicMock(return_value=create_prod_id(id='prod_123')))
    @mock.patch('stripe.Price.create', mock.MagicMock(return_value=create_prod_id(id='price_123')))
    def setUp(self):
        initial_user(self)
        self.shopA = Shop.objects.create(name='shopA')
        self.shopB = Shop.objects.create(name='shopB')
        self.product = Product.objects.create(name='product', price=3000)
        self.ticket0 = Ticket.objects.create(
            owner=self.user,
            kind=self.product,
            situation=Ticket.SITUATION_USABLE
        )

    def test_use_one_one(self):
        """1枚所持時に1枚利用 Ticketが均等に使われる場合"""

        self.user.ticket.use_by_count(self.shopA, 1, self.product)

        self.assertEqual(self.ticket0.stub.all().count(), 1)
        self.assertEqual(self.ticket0.stub.first().shop, self.shopA)

    def test_use_one_tw(self):
        """1枚所持時に2枚利用 Ticketが均等に使われる場合"""
        self.user.ticket.use_by_count(self.shopA, 2, self.product)

        self.assertEqual(self.ticket0.stub.all().count(), 2)
        self.assertEqual(self.ticket0.stub.first().shop, self.shopA)

    def test_use_two_two(self):
        """2枚所持時に2枚利用 Ticketが均等に使われる場合"""
        self.ticket1 = Ticket.objects.create(
            owner=self.user,
            kind=self.product,
            situation=Ticket.SITUATION_USABLE
        )
        self.user.ticket.use_by_count(self.shopA, 2, self.product)

        self.assertEqual(self.ticket0.stub.all().count(), 1)
        self.assertEqual(self.ticket1.stub.all().count(), 1)
        self.assertEqual(self.ticket1.stub.first().shop, self.shopA)

    def test_use_two_three(self):
        """2枚所持時に3枚利用 Ticketが均等に使われる場合"""
        self.ticket1 = Ticket.objects.create(
            owner=self.user,
            kind=self.product,
            situation=Ticket.SITUATION_USABLE
        )
        self.user.ticket.use_by_count(self.shopA, 3, self.product)

        self.assertEqual(self.ticket0.stub.all().count(), 2)
        self.assertEqual(self.ticket1.stub.all().count(), 1)
        self.assertEqual(self.ticket1.stub.first().shop, self.shopA)

    def test_use_two_three_two(self):
        """2枚所持時に3枚利用, さらに2枚利用 Ticketが均等に使われる場合"""
        self.ticket1 = Ticket.objects.create(
            owner=self.user,
            kind=self.product,
            situation=Ticket.SITUATION_USABLE
        )
        self.user.ticket.use_by_count(self.shopA, 3, self.product)
        self.user.ticket.use_by_count(self.shopB, 2, self.product)

        self.assertEqual(self.ticket0.stub.all().count(), 3)
        self.assertEqual(self.ticket1.stub.all().count(), 2)
        self.assertEqual(self.ticket1.stub.first().shop, self.shopA)
        self.assertEqual(Ticket.objects.get(pk=self.ticket0.pk).situation, Ticket.SITUATION_USED)

    def test_use_cant_use(self):
        """1枚持っているがアクティブ出ないので利用できない Ticketが均等に使われる場合"""
        self.ticket0.situation = Ticket.SITUATION_BEFORE
        self.ticket0.save()

        with self.assertRaises(ValueError):
            self.user.ticket.use_by_count(self.shopA, 3, self.product)


class UseTicketTestWithOneByOne(TestCase):

    def create_prod_id(id):
        class Prod_class():
            id = ""

            def __init__(self, pro):
                self.id = pro
        return Prod_class(id)

    @mock.patch('stripe.Product.create', mock.MagicMock(return_value=create_prod_id(id='prod_123')))
    @mock.patch('stripe.Price.create', mock.MagicMock(return_value=create_prod_id(id='price_123')))
    def setUp(self):
        initial_user(self)
        self.shopA = Shop.objects.create(name='shopA')
        self.shopB = Shop.objects.create(name='shopB')
        self.product = Product.objects.create(
            name='product',
            price=3000,
            usage=Product.SITUATION_ONE_BY_ONE
        )
        self.ticket0 = Ticket.objects.create(
            owner=self.user,
            kind=self.product,
            situation=Ticket.SITUATION_USABLE
        )

    def test_use_one_one(self):
        """1枚所持時に1枚利用 Ticketが一枚づつ使われる場合"""
        self.user.ticket.use_by_count(self.shopA, 1, self.product)

        self.assertEqual(self.product.usage, Product.SITUATION_ONE_BY_ONE)
        self.assertEqual(self.ticket0.stub.all().count(), 1)
        self.assertEqual(self.ticket0.stub.first().shop, self.shopA)

    def test_use_one_two_one(self):
        """1枚所持時に2枚利用その後1枚利用 Ticketが一枚づつ使われる場合"""
        self.user.ticket.use_by_count(self.shopA, 2, self.product)
        self.user.ticket.use_by_count(self.shopA, 1, self.product)

        self.assertEqual(self.ticket0.stub.all().count(), 3)
        self.assertEqual(self.ticket0.stub.first().shop, self.shopA)
        self.assertEqual(Ticket.objects.get(pk=self.ticket0.pk).situation, Ticket.SITUATION_USED)

    def test_use_one_two(self):
        """1枚所持時に3枚利用 Ticketが一枚づつ使われる場合"""
        self.user.ticket.use_by_count(self.shopA, 3, self.product)

        self.assertEqual(self.ticket0.stub.all().count(), 3)
        self.assertEqual(self.ticket0.stub.first().shop, self.shopA)
        self.assertEqual(Ticket.objects.get(pk=self.ticket0.pk).situation, Ticket.SITUATION_USED)

    def test_use_two_two(self):
        """2枚所持時に2枚利用 Ticketが一枚づつ使われる場合"""
        self.ticket1 = Ticket.objects.create(
            owner=self.user,
            kind=self.product,
            situation=Ticket.SITUATION_USABLE
        )
        self.user.ticket.use_by_count(self.shopA, 2, self.product)

        self.assertEqual(self.ticket0.stub.all().count(), 2)
        self.assertEqual(self.ticket1.stub.all().count(), 0)
        self.assertEqual(self.ticket0.stub.first().shop, self.shopA)

    def test_use_two_three(self):
        """2枚所持時に3枚利用 Ticketが一枚づつ使われる場合"""
        self.ticket1 = Ticket.objects.create(
            owner=self.user,
            kind=self.product,
            situation=Ticket.SITUATION_USABLE
        )
        self.user.ticket.use_by_count(self.shopA, 3, self.product)

        self.assertEqual(self.ticket0.stub.all().count(), 3)
        self.assertEqual(self.ticket1.stub.all().count(), 0)
        self.assertEqual(self.ticket0.stub.first().shop, self.shopA)
        self.assertEqual(Ticket.objects.get(pk=self.ticket0.pk).situation, Ticket.SITUATION_USED)

    def test_use_two_three_two(self):
        """2枚所持時に3枚利用, さらに2枚利用 Ticketが一枚づつ使われる場合"""
        self.ticket1 = Ticket.objects.create(
            owner=self.user,
            kind=self.product,
            situation=Ticket.SITUATION_USABLE
        )
        self.user.ticket.use_by_count(self.shopA, 3, self.product)
        self.user.ticket.use_by_count(self.shopB, 2, self.product)

        self.assertEqual(self.ticket0.stub.all().count(), 3)
        self.assertEqual(self.ticket1.stub.all().count(), 2)
        self.assertEqual(self.ticket0.stub.all()[0].shop, self.shopA)
        self.assertEqual(self.ticket0.stub.all()[1].shop, self.shopA)
        self.assertEqual(self.ticket0.stub.all()[2].shop, self.shopA)
        self.assertEqual(self.ticket1.stub.all()[0].shop, self.shopB)
        self.assertEqual(self.ticket1.stub.all()[1].shop, self.shopB)
        self.assertEqual(Ticket.objects.get(pk=self.ticket0.pk).situation, Ticket.SITUATION_USED)
        self.assertEqual(Ticket.objects.get(pk=self.ticket1.pk).situation, Ticket.SITUATION_USABLE)

    def test_use_cant_use(self):
        """1枚持っているがアクティブ出ないので利用できない Ticketが一枚づつ使われる場合"""
        self.ticket0.situation = Ticket.SITUATION_BEFORE
        self.ticket0.save()

        with self.assertRaises(ValueError):
            self.user.ticket.use_by_count(self.shopA, 3, self.product)
