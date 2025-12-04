from django.test import TestCase
from apps.core.models import User, Ticket

from ..setup import initial_get_product


class UserModelTests(TestCase):

    def test_is_empty(self):
        """初期状態では何も登録されていないことをチェック"""
        saved_users = User.objects.all()
        self.assertEqual(saved_users.count(), 0)

    def test_is_count_one(self):
        """1つレコードを適当に作成すると、レコードが1つだけカウントされることをテスト"""
        user = User(lineUserID='test_username')
        user.save()
        saved_users = User.objects.all()
        self.assertEqual(saved_users.count(), 1)

    def test_saving_and_retrieving_user(self):
        """内容を指定してデータを保存し、すぐに取り出した時に保存した時と同じ値が返されることをテスト"""
        user = User()
        lineUserID = 'test_username'
        user.lineUserID = lineUserID
        user.save()

        saved_users = User.objects.all()
        actual_user = saved_users[0]

        self.assertEqual(actual_user.lineUserID, lineUserID)

    def test_create_ticket_from_user(self):
        """ ユーザーからのチケットチケット作成テスト """
        user = User.objects.create(lineUserID='test_username')
        products = initial_get_product()

        boughts = [
            {
                'quantity': 1,
                'kind': products[0],
                'is_pay': True,
            },
            {
                'quantity': 2,
                'kind': products[1],
                'is_pay': False,
            },
        ]

        user.create_ticket(boughts)
        tickets = Ticket.objects.all()

        self.assertEqual(tickets.count(), 3, "チケットの登録枚数が3")
        self.assertEqual(tickets.first().owner, user, "チケットの主がユーザーである")
        self.assertEqual(user.ticket.all().count(), tickets.count(), "チケットの主がユーザーであるの逆引き")
